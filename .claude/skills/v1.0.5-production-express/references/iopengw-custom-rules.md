# iopengw Custom Rules

This file contains system-specific rules and customizations for the `iopengw` gateway system.

## System Overview

`iopengw` is a gateway system that acts as a boundary between internal systems and external channels. It handles HTTPS communication with external services.

## Log Query Keywords

For the `iopengw` system, use these log keywords instead of the defaults:

| Keyword | Log Type | Example |
|---------|----------|---------|
| `message` | Message processing logs | `iopengw-message.log` |
| `digest` | Digest/summary logs | `iopengw-digest.log` |

**Do NOT query:** `biz`, `integration`, or `error` logs for iopengw.

### Query Examples

```
# Query message logs
CallMcpTool: server_name="antlog" tool_name="queryAppLogContent" arguments={
  "appName": "iopengw",
  "startTime": "<startTime>",
  "endTime": "<endTime>",
  "query": "'<traceId>'",
  "logPathKeyword": "message",
  "resultLimitPerLog": 100
}

# Query digest logs
CallMcpTool: server_name="antlog" tool_name="queryAppLogContent" arguments={
  "appName": "iopengw",
  "startTime": "<startTime>",
  "endTime": "<endTime>",
  "query": "'<traceId>'",
  "logPathKeyword": "digest",
  "resultLimitPerLog": 100
}
```

## Message Log Types

When analyzing iopengw `message` logs, look for these specific message types to understand the request/response flow:

| Message Type | Direction | Description |
|--------------|-----------|-------------|
| `INBOUND_REQUEST` | Upstream → iopengw | Request received from the upstream (calling) system |
| `OUTBOUND_REQUEST` | iopengw → External | HTTPS request sent from iopengw to the external channel |
| `OUTBOUND_RESPONSE` | External → iopengw | HTTPS response received from the external channel |
| `INBOUND_RESPONSE` | iopengw → Upstream | Response sent back to the upstream (calling) system |

## Message Flow Analysis

When debugging issues involving iopengw, analyze the message logs in this order:

```
INBOUND_REQUEST → OUTBOUND_REQUEST → OUTBOUND_RESPONSE → INBOUND_RESPONSE
```

### What to Look For in Each Message Type

#### INBOUND_REQUEST
- **Source**: Upstream system that initiated the call
- **Content**: Original request payload from upstream
- **Key Info**: Request ID, endpoint, headers, body

#### OUTBOUND_REQUEST
- **Destination**: External channel (HTTPS endpoint)
- **Content**: Transformed request sent to external service
- **Key Info**: URL, method, headers, payload, timeout settings

#### OUTBOUND_RESPONSE
- **Source**: External channel
- **Content**: Response from external service
- **Key Info**: HTTP status code, response body, error codes, latency
- **Error Indicators**: Non-2xx status codes, timeout errors, connection failures

#### INBOUND_RESPONSE
- **Destination**: Upstream system
- **Content**: Final response sent back to caller
- **Key Info**: Transformed response, error mapping, status code

## Debugging Workflow for iopengw

1. **Query message logs** using the `message` keyword
2. **Identify all four message types** for the traceId
3. **Check OUTBOUND_RESPONSE** for external channel errors
4. **Correlate with upstream system** to see how it handles iopengw responses

## Common Patterns

### External Channel Timeout
```
INBOUND_REQUEST: Received from upstream
OUTBOUND_REQUEST: Sent to external channel
OUTBOUND_RESPONSE: Timeout/Connection error
INBOUND_RESPONSE: Error response to upstream
```

### External Channel Error Response
```
INBOUND_REQUEST: Received from upstream
OUTBOUND_REQUEST: Sent to external channel
OUTBOUND_RESPONSE: HTTP 4xx/5xx from external
INBOUND_RESPONSE: Mapped error to upstream
```

### Successful Flow
```
INBOUND_REQUEST: Received from upstream
OUTBOUND_REQUEST: Sent to external channel
OUTBOUND_RESPONSE: HTTP 2xx from external
INBOUND_RESPONSE: Success response to upstream
```

## Integration with Upstream Systems

When iopengw is the downstream system:
1. Check how the upstream system handles `INBOUND_RESPONSE` from iopengw (from logs)
2. Look for timeout configurations in upstream logs
3. Verify error handling for different iopengw response codes from log evidence
4. Check if upstream has retry logic for iopengw calls (from logs)
