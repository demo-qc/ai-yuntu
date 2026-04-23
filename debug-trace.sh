#!/usr/bin/env bash
# Trigger the production-express debug routine for a given trace.
# Usage: ./debug-trace.sh <trace_id> <app_name> [output_type]

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <trace_id> <app_name> [output_type]" >&2
  exit 1
fi

TRACE_ID="$1"
APP_NAME="$2"
OUTPUT_TYPE="${3:-basic}"

cd "$(dirname "$0")"

PROMPT=$(cat <<EOF
Debug this production issue.
traceId: ${TRACE_ID}
appName: ${APP_NAME}
outputType: ${OUTPUT_TYPE}
EOF
)

exec claude \
  -p "$PROMPT" \
  --permission-mode bypassPermissions \
  --output-format stream-json \
  --verbose
