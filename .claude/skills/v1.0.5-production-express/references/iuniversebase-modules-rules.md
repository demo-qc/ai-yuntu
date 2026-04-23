# iuniversebase Modules Custom Rules

This file contains system-specific rules for systems that are deployed as modules within `iuniversebase`.

## Affected Systems

The following systems are modules deployed within `iuniversebase`:

| Module Name | Description | Deployed As |
|-------------|-------------|-------------|
| `inova` | Nova payment module | Module in iuniversebase |
| `iorch` | Orchestration module | Module in iuniversebase |
| `itradecore` | Trade core module | Module in iuniversebase |

## Critical Rule: appName for Log Queries

**For these systems, the appName used in antlog/yuntu differs from the module name:**

| Module Name | Use for antlog/yuntu appName |
|-------------|------------------------------|
| `inova` | `iuniversebase` |
| `iorch` | `iuniversebase` |
| `itradecore` | `iuniversebase` |

### Why This Happens

These systems are deployed as modules within the `iuniversebase` application. Therefore:
- **antlog** recognizes them under the parent application name `iuniversebase`
- **yuntu** shows them as `iuniversebase` in trace trees

## Log Query Rules

### Querying Logs for inova, iorch, or itradecore

When querying antlog for these systems, **ALWAYS use `iuniversebase` as the appName**:

```
# CORRECT: Query logs for inova/iorch/itradecore
CallMcpTool: server_name="antlog" tool_name="queryAppLogContent" arguments={
  "appName": "iuniversebase",  // NOT "inova", "iorch", or "itradecore"
  "startTime": "<startTime>",
  "endTime": "<endTime>",
  "query": "'<traceId>'",
  "logPathKeyword": "biz",
  "resultLimitPerLog": 100
}
```

### Default Log Keywords

For `iuniversebase` and its modules, use the standard log keywords:
- `biz` - Business service logs
- `integration` - Integration logs
- `error` - Error logs

## Yuntu Trace Tree Analysis

### Critical: Internal Module Communication

**Modules within iuniversebase can communicate with each other directly.** This means the yuntu trace tree may show a simplified view while the actual internal flow involves multiple modules.

#### Trace Tree Simplification

The yuntu trace tree shows `iuniversebase` as a single node, but internally the flow may pass through multiple modules:

```
Yuntu Trace Tree (Simplified):
iexpprod → iuniversebase → ifinflux → iopengw

Actual Internal Flow (What really happens):
iexpprod → iorch → inova → ifinflux → iopengw
```

#### Why This Happens

- All modules (iorch, inova, itradecore) are deployed in the same JVM/container
- Internal module calls are local method invocations, not RPC calls
- Yuntu only traces external RPC/service calls
- Integration logs contain the actual module-to-module call information

### Identifying the Actual Module Flow

When analyzing a trace that involves iuniversebase:

1. **Query iuniversebase integration logs** - These show internal module calls
2. **Look for module identifiers in logs**:
   - `IORCH` → iorch module
   - `INOVA` → inova module
   - `ITRADECORE` → itradecore module
3. **Check integration log entries** for:
   - `[IORCH] calling [INOVA]` - iorch calling inova
   - `[INOVA] calling [ifinflux]` - inova calling external ifinflux

### Example: Tracing Internal Module Flow

**Scenario**: Yuntu trace shows:
```
iuniversebase → ifinflux → iopengw
```

**Step 1**: Query iuniversebase integration logs:
```
CallMcpTool: server_name="antlog" tool_name="queryAppLogContent" arguments={
  "appName": "iuniversebase",
  "startTime": "<startTime>",
  "endTime": "<endTime>",
  "query": "'<traceId>'",
  "logPathKeyword": "integration",
  "resultLimitPerLog": 100
}
```

**Step 2**: Analyze integration logs for module identifiers:
```
[2026-03-31 10:00:01] [IORCH] FlowOrchestrator.execute - Starting payment flow
[2026-03-31 10:00:02] [IORCH] calling downstream: INOVA.processPayment
[2026-03-31 10:00:02] [INOVA] PaymentProcessor.process - Processing payment
[2026-03-31 10:00:03] [INOVA] calling downstream: ifinflux.sendRequest
```

**Step 3**: Reconstruct the actual flow:
```
Actual Flow:
iorch → inova → ifinflux → iopengw
```

**Key Insight**: The integration logs of iorch show it calling inova, and inova's logs show it calling ifinflux. This reveals the complete internal module flow.

### Identifying the Module in Trace Tree

When analyzing the yuntu trace tree:
1. Look for `iuniversebase` in the trace tree
2. Query integration logs to see internal module calls
3. The actual module (inova, iorch, or itradecore) may be indicated by:
   - Module identifiers in integration logs (IORCH, INOVA, ITRADECORE)
   - Package/class names in stack traces
   - Log file names or content
   - RPC interface names

### Example Trace Tree Interpretation

```
iexpprod
  → iacquirefront
    → iuniversebase  ← Query integration logs to identify internal module flow
      → ifinflux
        → iopengw
```

**How to identify the actual internal flow:**
1. Query `iuniversebase` **integration logs** for the traceId
2. Look for module identifiers:
   - `[IORCH]` → iorch module
   - `[INOVA]` → inova module
   - `[ITRADECORE]` → itradecore module
3. Look at the class names/package names in the logs:
   - `com.ant.inova.*` → inova module
   - `com.ant.iorch.*` → iorch module
   - `com.ant.itradecore.*` → itradecore module
4. Check the RPC interface or method names
5. Reconstruct the actual module flow from integration log entries

## Debugging Workflow for iuniversebase Modules

1. **Identify iuniversebase in trace tree** - Query yuntu trace tree
2. **Query iuniversebase logs** - Use `iuniversebase` as appName
3. **Query integration logs for internal module flow** - Identify module-to-module calls
4. **Determine the specific module(s)** - Check package names, class names, or RPC interfaces
5. **Continue standard log-based debugging** - Apply the normal error tracing workflow

### Detailed Workflow for Multi-Module Tracing

When the trace tree shows `iuniversebase`, follow these steps to trace the actual internal module flow:

1. **Query yuntu trace tree** to see the external call chain
2. **Query iuniversebase integration logs** with the traceId:
   ```
   CallMcpTool: server_name="antlog" tool_name="queryAppLogContent" arguments={
     "appName": "iuniversebase",
     "startTime": "<startTime>",
     "endTime": "<endTime>",
     "query": "'<traceId>'",
     "logPathKeyword": "integration",
     "resultLimitPerLog": 100
   }
   ```
3. **Analyze integration logs** to find:
   - Module identifiers (IORCH, INOVA, ITRADECORE)
   - Calls between modules
   - Calls from modules to external systems
4. **Reconstruct the actual flow** from integration log entries
5. **Identify which module(s) to investigate** based on where the error occurred

## Common Scenarios

### Scenario 1: Error in inova Module

```
Trace tree shows:
iexpprod → iuniversebase → ipaycore

Logs show:
com.ant.inova.service.PaymentService.process() - ERROR

Action:
1. Query iuniversebase logs
2. Identify inova module from package name
3. Trace error through logs
```

### Scenario 2: Error in iorch Module

```
Trace tree shows:
iexpprod → iuniversebase → ipaycore

Logs show:
com.ant.iorch.orchestrator.FlowOrchestrator.execute() - ERROR

Action:
1. Query iuniversebase logs
2. Identify iorch module from package name
3. Trace error through logs
```

### Scenario 3: Error in itradecore Module

```
Trace tree shows:
iexpprod → iuniversebase → ipaycore

Logs show:
com.ant.itradecore.trade.TradeProcessor.process() - ERROR

Action:
1. Query iuniversebase logs
2. Identify itradecore module from package name
3. Trace error through logs
```

### Scenario 4: Multi-Module Flow (iorch → inova)

```
Yuntu trace tree shows:
iexpprod → iuniversebase → ifinflux → iopengw

Integration logs show:
[IORCH] FlowOrchestrator.execute - Starting payment flow
[IORCH] calling downstream: INOVA.processPayment
[INOVA] PaymentProcessor.process - Processing payment
[INOVA] calling downstream: ifinflux.sendRequest
[INOVA] Received error from ifinflux: PROCESS_FAIL

Actual flow reconstructed:
iexpprod → iorch → inova → ifinflux → iopengw

Action:
1. Query iuniversebase integration logs
2. Identify the multi-module flow (iorch → inova)
3. Determine which module caused the error (inova received error from ifinflux)
4. Trace error handling through logs
```

## Quick Reference Table

| Task | What to Use |
|------|-------------|
| Query antlog for inova/iorch/itradecore | `appName = "iuniversebase"` |
| Find in yuntu trace tree | Look for `iuniversebase` |
| Identify specific module | Check package/class names in logs |
| Identify internal module flow | Query integration logs for module identifiers (IORCH, INOVA, ITRADECORE) |
| Reconstruct actual flow | Analyze integration log entries for module-to-module calls |

## Decision Flow

```
Is the appName one of: inova, iorch, itradecore?
    ↓ YES
Use "iuniversebase" for:
  - antlog queries (appName parameter)
  - yuntu trace tree lookups
```
