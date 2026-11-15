#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-cve126910}"
export PYTHONUNBUFFERED=1

LABEL="CVE-2026-126910"
WITNESS="CVE-2026-126910-TYPECONF-WITNESS"
LOCK_PID=""
LOCK_LOG="/tmp/cve126910-slot.log"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

release_lock() {
  if [[ -n "${LOCK_PID}" ]]; then
    kill "${LOCK_PID}" 2>/dev/null || true
    wait "${LOCK_PID}" 2>/dev/null || true
    LOCK_PID=""
  fi
  rm -f "${LOCK_LOG}"
}

fail_setup() {
  local reason="$1"
  if [[ ! -f poc-last-run.txt ]] || ! tail -n 1 poc-last-run.txt | grep -qE '^(SUCCESS|FAIL) '; then
    echo "FAIL ${LABEL} ${reason} ${WITNESS}" | tee poc-last-run.txt
  fi
  down
  release_lock
  exit 1
}

finished() {
  [[ -f poc-last-run.txt ]] && tail -n 1 poc-last-run.txt | grep -qE '^(SUCCESS|FAIL) '
}

acquire_lock() {
  rm -f "${LOCK_LOG}"
  python3 -u - << 'PY' >"${LOCK_LOG}" 2>&1 &
import fcntl
import signal
import sys
import time
from pathlib import Path

deadline = time.time() + 40 * 60
slots = [Path("/tmp/chrome-lab-slot-1.lock"), Path("/tmp/chrome-lab-slot-2.lock")]
while time.time() < deadline:
    for slot in slots:
        handle = slot.open("a+")
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            handle.close()
            continue
        print(f"ACQUIRED {slot.name}", flush=True)
        signal.signal(signal.SIGTERM, lambda *_signum, _frame: sys.exit(0))
        signal.signal(signal.SIGINT, lambda *_signum, _frame: sys.exit(0))
        try:
            signal.pause()
        except AttributeError:
            while True:
                time.sleep(3600)
        sys.exit(0)
    print("slots-busy", flush=True)
    time.sleep(20)
print("TIMEOUT", flush=True)
sys.exit(1)
PY
  LOCK_PID=$!
  local waited=0
  while [[ "${waited}" -lt 2500 ]]; do
    if grep -q '^ACQUIRED ' "${LOCK_LOG}" 2>/dev/null; then
      echo "== $(grep '^ACQUIRED ' "${LOCK_LOG}" | tail -n 1) =="
      return 0
    fi
    if ! kill -0 "${LOCK_PID}" 2>/dev/null; then
      echo "== chrome slot lock failed =="
      cat "${LOCK_LOG}" || true
      return 1
    fi
    sleep 1
    waited=$((waited + 1))
  done
  return 1
}

trap 'down; release_lock' EXIT
down
rm -f poc-last-run.txt
if ! acquire_lock; then
  fail_setup "chrome-slot-timeout"
fi

chmod +x poc.py start.sh run.sh

run_without_publish() {
  # Host 18630 is taken by a foreign process. The oracle only needs
  # container loopback; compose still documents 127.0.0.1:18630:18630.
  echo "== host 18630 busy; docker run without publish =="
  docker rm -f "${COMPOSE_PROJECT_NAME}-lab" >/dev/null 2>&1 || true
  docker run --rm --name "${COMPOSE_PROJECT_NAME}-lab" \
    --init \
    --shm-size=2g \
    --security-opt seccomp:unconfined \
    -v "${PWD}:/out" \
    -v "${PWD}/poc.py:/lab/poc.py:ro" \
    -v "${PWD}/poc.html:/lab/poc.html:ro" \
    -e PYTHONUNBUFFERED=1 \
    --label lab=CVE-2026-126910 \
    --label cve=CVE-2026-126910 \
    cve-2026-126910:lab
}

echo "== docker compose up --build =="
up_ok=0
for attempt in $(seq 1 2); do
  set +e
  up_log="$(mktemp)"
  docker compose -p "${COMPOSE_PROJECT_NAME}" up --build --abort-on-container-exit --exit-code-from lab \
    > >(tee "${up_log}") 2>&1
  rc=$?
  set -e
  if finished; then
    up_ok=1
    echo "lab-finished attempt=${attempt} compose_rc=${rc}"
    rm -f "${up_log}"
    break
  fi
  if grep -q 'address already in use' "${up_log}"; then
    rm -f "${up_log}"
    down
    set +e
    run_without_publish
    rc=$?
    set -e
    if finished; then
      up_ok=1
      echo "lab-finished attempt=${attempt} docker_run_rc=${rc}"
      break
    fi
  else
    rm -f "${up_log}"
  fi
  echo "compose-up-retry attempt=${attempt} compose_rc=${rc}"
  sleep 8
  down
done
if [[ "${up_ok}" != 1 ]]; then
  echo "== compose logs (no oracle line) =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=160 || true
  fail_setup "compose-up-failed"
fi

echo "== oracle =="
tail -n 1 poc-last-run.txt
down
release_lock
trap - EXIT
exit 0
