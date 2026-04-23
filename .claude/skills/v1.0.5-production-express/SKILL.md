---
name: production-debug-express
description: Debug production issues through log-only analysis using antlog and yuntu MCP. An express version of production-debug that eliminates codebase investigation — traces are debugged PURELY from log evidence. Use when you need rapid root cause identification from logs alone, without requiring local codebase access. Investigates not only where errors originated but also WHY downstream systems threw errors to determine the true root cause. Use when users ask to debug production, trace an error, investigate a failure, or troubleshoot a production issue, and do NOT need code-level analysis.
---

# Production Issue Debugging (Express)

Debug production issues through **log-only analysis** to identify root causes with clear evidence. This express skill eliminates codebase investigation entirely — all debugging is performed purely from antlog and yuntu MCP queries. It goes beyond identifying error sources — it investigates WHY downstream systems threw errors to determine the true root cause.

## Critical: Task Isolation

**Each debugging task must be treated as completely independent.**
- **DO NOT reference** any previous debugging sessions or reports
- **DO NOT carry over** assumptions, conclusions, or patterns from past investigations
- **Start with ZERO prior knowledge** — only the traceId, appName, and user-provided context matter

Every production issue is unique. Always investigate from first principles.

## When to Use

- Business logic errors in production
- Unexpected service behavior or data inconsistency
- Workflow failures or integration problems between services
- Issues where log evidence is sufficient to identify root cause
- Rapid triage when codebase access is unavailable or unnecessary

## Prerequisites

Before starting, ensure you have:
- **traceId** of the failing request
- **appName** (application name where the error was observed) — **REQUIRED**
- **outputType** (optional) — `basic` or `full` (default: `full`)

### Required MCP Servers

| MCP Server | Purpose |
|------------|---------|
| **antlog** | Query application logs, trace IDs, error details |
| **yuntu** | Query service call chains and trace trees |
| **yuque** | Upload debug reports to Yuque for sharing (`full` mode only) |

**If MCP servers are not available**, prompt user to install before proceeding.

### Optional Parameter: outputType

Controls the token usage of the debugging workflow. The purpose of `basic` mode is to **reduce token usage**:

| Value | Token Usage Optimization | Description |
|-------|-------------------------|-------------|
| `full` | None | **(Default)** Complete debug report with all sections. Report file created and uploaded to Yuque. |
| `basic` | 1. Reduced output content<br>2. No file output<br>3. Skip Yuque upload | **No report file is created.** Only Issue Summary and Error Classification are output directly in chat. |

If the user does not specify `outputType`, treat it as `full`.

### Required Parameter: appName

**If appName is NOT provided**, see `references/RULE.md` §Required Parameters.

**Special cases** (see `references/RULE.md` §System-Specific Rules):
- `inova`, `iorch`, `itradecore` → Use `iuniversebase` for antlog/yuntu queries
- `iopengw` → Use `message` and `digest` log keywords (not standard)

## Debugging Workflow

### Phase 0: Validate Prerequisites

**Step 0A: Verify MCP availability**

Check that `antlog` and `yuntu` MCP servers are available. If missing, prompt user to install.

**Step 0B: Verify appName is provided**

If appName is missing, ask the user and wait for response before proceeding.

### Phase 1: Gather Log Evidence

**Step 1: Extract time range from traceId**

Call `antlog.getTimeRangeOfTraceId` with the traceId. See `references/RULE.md` §Workflow Reference → Phase 1 for call details.

**Validate traceId**: If the result does not contain valid `startTime` and `endTime`, **STOP IMMEDIATELY** — see `references/RULE.md` §Required Parameters → traceId for the invalid traceId message template.

If valid, add **5 minutes** to `endTime` for log latency. Record `startTime` as fallback `errorTime`.

**Step 2 + 3: Gather log evidence and trace tree in parallel**

> **EFFICIENCY**: Execute all log queries and trace tree query in **parallel**. See `references/RULE.md` §Workflow Reference → Phase 1 for full call details.

- **Error logs** (`logPathKeyword: "error"`): Identify stack traces, error codes, exceptions. Extract `errorTime` from earliest error entry.
- **Biz logs** (`logPathKeyword: "biz"`): Understand business flow — request, response, decisions.
- **Integration logs** (`logPathKeyword: "integration"`): Identify downstream calls and responses.
- **Trace tree** (`yuntu.queryYuntuTraceTree`): Identify all services in call chain.

Use appropriate log keywords for the system — see `references/RULE.md` §Log Query Rules.

**Handling large antlog output**: Use the standard parsing template from `references/RULE.md` §Log Parsing Template.

### Phase 1B: Iterative Downstream Error Tracing

**Step 4: Trace errors through downstream systems**

See `references/RULE.md` §Error Tracing Rules for detailed rules.

1. Analyze current system logs — was error generated locally or passed from downstream?
2. If from downstream: Identify immediate downstream `appName` and continue tracing
3. **Check boundary condition**: If downstream is `iopengw` → Extract error from iopengw logs and STOP
4. Repeat until error origin is found

Query downstream system logs in parallel when multiple downstream systems are identified.

**Step 5: Distinguish handled vs unhandled errors**

See `references/RULE.md` §Distinguish Handled vs Unhandled Errors. An error is only the root cause if it was **unhandled** and caused the flow to fail.

**Step 6: Investigate WHY the error was thrown**

1. Query the system's logs for error details
2. Analyze log context (request parameters, response data, error codes) to understand business logic
3. Identify conditions that trigger the error from log patterns
4. Cross-reference error codes across upstream/downstream logs

> **EARLY TERMINATION CHECKPOINT**: After completing Phase 1B, ask yourself: (1) Do I know which system caused the error? (2) Do I know WHY? (3) Do I have complete log evidence? If YES to all three → **skip directly to Phase 4**. Do NOT query upstream systems or do additional filtered log searches — you already have the answer. See `references/RULE.md` §Adaptive Depth Rules → Early Termination After Root Cause Found.

### Phase 2: Root Cause Analysis

**Step 7**: Formulate 2-3 hypotheses based on verified log evidence.

**Step 8**: Validate each hypothesis against log evidence and error tracing results.

**Step 9**: Confirm root cause — must have clear explanation, verified log evidence, and identified error origin system.

> **Note**: Since this is an express (log-only) skill, root cause analysis is based on log evidence alone. If deeper code-level investigation is needed, recommend using the full `production-debug` skill.

### Phase 3: Error Classification

Classify the error — see `references/RULE.md` §Error Classification Framework for the hierarchy and decision tree.

### Phase 4: Generate Output Report

**Step 10: Create debug report**

> **TOKEN OPTIMIZATION**: If `outputType` is `basic`, **skip Step 10 and Step 11**. No report file is created. Proceed directly to outputting the summary in chat.

If `outputType` is `full`, create output file at:
```
<skill_base_path>/output/<flow>/<error_type>/<payment_method>/<errorTime>_<traceId>_<appName>_debug_report.md
```

Path parameters (defaults: `GENERIC_FLOW` / `UNKNOWN_ERROR` / `GENERIC`):
- **errorTime**: `YYYYMMDDHHmmss` from earliest error log (fallback: trace `startTime`)
- **flow**: Business flow (e.g., `pay`, `refund`, `inquiry`)
- **error_type**: Error code (e.g., `TIMEOUT`, `ORDER_NOT_FOUND`)
- **payment_method**: Payment method (e.g., `ALIPAY_CN`, `CARD`)

Use the Full Report Template — see `references/RULE.md` §Output File Rules → Report Structure Template.

**Step 11: Upload report to Yuque**

> **TOKEN OPTIMIZATION**: If `outputType` is `basic`, **skip this step** — no file was created.

If `outputType` is `full`, upload the report to Yuque. See `references/RULE.md` §Workflow Reference → Phase 4: Yuque Upload Steps for full call details.

**Step 11c: Output summary to the user**

After completing applicable steps, provide a **concise summary** — **ONLY** Issue Summary + Error Classification, using the **markdown table format** from the Report Structure Template in `references/RULE.md`. Nothing else in the chat.

**If `full` mode** — append the Yuque link:
```
📄 Full report: <yuque_doc_url>
```

**If `basic` mode** — no link (no file was created).

**DO NOT include** Log Evidence, Root Cause, Fix Recommendation, or Investigation Limitations in the chat summary. These belong in the full report on Yuque.

**If yuque MCP is not available**: Skip upload and note in Investigation Limitations. The local file is still available.

## Constraints

All constraints, rules, and quality standards are defined in `references/RULE.md`.

**Key rules:**
- Always ensure appName is provided before starting
- Always validate traceId after getTimeRangeOfTraceId — STOP if invalid
- Always retry MCP calls up to 3 times on failure
- Always treat `iopengw` as STRICT BOUNDARY
- Always investigate WHY downstream system threw the error
- Always create output markdown file when outputType is `full`; skip when `basic`
- Always upload debug report to Yuque when outputType is `full` and yuque MCP is available; skip when `basic`
- Always set Yuque documents to public (`"1"`)
- Always output ONLY Issue Summary + Error Classification (+ Yuque link for `full`) as chat summary
- Always document investigation limitations
- This is a log-only skill — **NEVER search or read codebases** during debugging

**Efficiency rules:**
- Always parallelize independent tool calls (log queries, downstream log queries)
- Always query error, biz, AND integration logs in parallel
- Never read MCP tool JSON schemas at runtime — parameters are documented in the skill
- Stop making additional queries once root cause is fully identified — see `references/RULE.md` §Early Termination After Root Cause Found
- Use log parsing templates from `references/RULE.md` §Log Parsing Template for large antlog output

## Output

**outputType=`full`**: Debug report at `<skill_base_path>/output/<flow>/<error_type>/<payment_method>/<errorTime>_<traceId>_<appName>_debug_report.md`, uploaded to `https://yuque.antfin.com/sean.lim/pgz2ru` (public).

**outputType=`basic`**: No report file. Issue Summary and Error Classification output directly in chat.
