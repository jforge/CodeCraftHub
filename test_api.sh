#!/bin/sh
# Run the API steps against a copy of courses.json in /tmp.
# The courses.json file in this project is not changed.

set -eu

cd "$(dirname "$0")"

DATA_COPY="/tmp/codecrafthub-courses.json"
PORT="${COURSES_PORT:-5000}"
BASE_URL="http://localhost:${PORT}"
SERVER_LOG="/tmp/codecrafthub-test-server.log"

if [ -x .venv/bin/python ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

echo
echo "=========================================="
echo "  CodeCraftHub API test"
echo "=========================================="
echo

echo "Copying courses.json to ${DATA_COPY}"
cp courses.json "$DATA_COPY"
LOCAL_BEFORE=$(cksum courses.json)
echo "The API will use the copy. The local example file stays in place."

export COURSES_FILE="$DATA_COPY"
export COURSES_PORT="$PORT"
export COURSES_DEBUG="false"

echo "Starting the API on ${BASE_URL}"
"$PYTHON" app.py >"$SERVER_LOG" 2>&1 &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "Waiting until the API answers"
ready=0
attempt=0
while [ "$attempt" -lt 50 ]; do
  if curl -sf "$BASE_URL/api/courses" >/dev/null 2>&1; then
    ready=1
    break
  fi
  attempt=$((attempt + 1))
  sleep 0.2
done

if [ "$ready" -ne 1 ]; then
  echo "The API did not start. See ${SERVER_LOG}"
  exit 1
fi

run_step() {
  step_name=$1
  shift
  echo
  echo "==== ${step_name} ===="

  response=$(curl -sS -w "\n%{http_code}" "$@")
  status=$(printf '%s\n' "$response" | tail -n 1)
  body=$(printf '%s\n' "$response" | sed '$d')

  printf '%s\n' "$body" | "$PYTHON" -m json.tool --indent 2
  echo "HTTP status: ${status}"
  echo
}

show_stats() {
  run_step "Statistics after ${1}" \
    "${BASE_URL}/api/courses/stats"
}

run_step "1. Get all courses" \
  "${BASE_URL}/api/courses"

run_step "2. Create a course" \
  -X POST "${BASE_URL}/api/courses" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, and API design.",
    "target_date": "2026-12-31",
    "status": "Not Started"
  }'
show_stats "create"

run_step "3. Get course ID 1" \
  "${BASE_URL}/api/courses/1"

run_step "4. Update course ID 1" \
  -X PUT "${BASE_URL}/api/courses/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, API design, and testing.",
    "target_date": "2026-12-31",
    "status": "In Progress"
  }'
show_stats "update"

run_step "5. Get all courses again" \
  "${BASE_URL}/api/courses"

run_step "6. Delete course ID 1" \
  -X DELETE "${BASE_URL}/api/courses/1"
show_stats "delete"

run_step "7. Confirm that course ID 1 was deleted" \
  "${BASE_URL}/api/courses/1"

LOCAL_AFTER=$(cksum courses.json)
if [ "$LOCAL_BEFORE" != "$LOCAL_AFTER" ]; then
  echo "The local courses.json file changed. That should not happen."
  exit 1
fi

echo "Finished. Local courses.json is unchanged."
echo "The working copy is ${DATA_COPY}"
