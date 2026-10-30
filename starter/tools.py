"""The agent's 'skills'.

Each tool is a thin wrapper that shells out to a standard, off-the-shelf
security tool (nmap, whatweb, ffuf, sqlmap) and returns its output. The agent
decides *which* to run and interprets the results; the tools themselves do the
work. Two design rules worth pointing out to students:

  1. The target host is fixed from config — the model never supplies it. The
     model only chooses *what* to test (ports, paths, params). This is scope
     control (see scope.py).

  2. Every model-supplied argument is validated against a strict pattern before
     it touches a subprocess, and we never use shell=True. That blocks the
     model from injecting shell metacharacters — the same command-injection
     defense they'll be testing the target for.
"""

import os
import re
import shutil
import subprocess
import tempfile

try:
    import requests  # nice-to-have; http_request falls back to urllib if absent
except Exception:
    requests = None

from . import config, scope
from .report import FINDINGS

# ---- validation helpers -----------------------------------------------------

_PORTS_RE = re.compile(r"^(top1000|[0-9]{1,5}(?:[-,][0-9]{1,5})*)$")
_PATH_RE = re.compile(r"^/[A-Za-z0-9/_.\-~%?=&]*$")
_PARAM_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")
_WORDLISTS = {
    "common": os.path.join(os.path.dirname(__file__), "wordlists", "common.txt"),
}


def _run(argv: list[str]) -> str:
    """Run a command (no shell) with a timeout and truncate the output."""
    if shutil.which(argv[0]) is None:
        return f"[tool '{argv[0]}' is not installed in this environment]"
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=config.TOOL_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return f"[{argv[0]} timed out after {config.TOOL_TIMEOUT}s]"
    out = (proc.stdout or "") + (proc.stderr or "")
    if len(out) > config.OUTPUT_TRUNC:
        out = out[: config.OUTPUT_TRUNC] + "\n...[truncated]..."
    return out.strip() or "[no output]"


# ---- the tools --------------------------------------------------------------

def port_scan(ports: str = "top1000") -> str:
    """nmap service/version scan of the fixed target host."""
    if not _PORTS_RE.match(ports):
        return "Invalid 'ports'. Use 'top1000' or a list like '80,443,8080'."
    base = ["nmap", "-Pn", "-sV"]
    scan = ["--top-ports", "1000"] if ports == "top1000" else ["-p", ports]
    return _run(base + scan + [config.TARGET_HOST])


def web_fingerprint() -> str:
    """Identify the web stack of the target (whatweb)."""
    return _run(["whatweb", "--color=never", config.TARGET_URL])


def content_discovery(wordlist: str = "common") -> str:
    """Directory/file brute force against the target (ffuf)."""
    path = _WORDLISTS.get(wordlist)
    if not path or not os.path.exists(path):
        return f"Unknown wordlist {wordlist!r}. Available: {list(_WORDLISTS)}"
    argv = [
        "ffuf", "-s", "-w", path,
        "-u", config.TARGET_URL + "/FUZZ",
        "-mc", "200,204,301,302,307,401,403",
        "-t", "20",
    ]
    if config.TARGET_COOKIE:
        argv += ["-H", f"Cookie: {config.TARGET_COOKIE}"]
    return _run(argv)


def http_request(path: str = "/", method: str = "GET", body: str = "") -> str:
    """Send a single HTTP request to a path on the target so the agent can
    probe an endpoint manually."""
    method = method.upper()
    if method not in {"GET", "POST", "PUT", "DELETE", "HEAD"}:
        return "Invalid method."
    if not _PATH_RE.match(path):
        return "Invalid path. Must start with '/' and contain URL-safe chars."
    url = scope.target_url(path)  # raises/validates scope
    hdr = {"Cookie": config.TARGET_COOKIE} if config.TARGET_COOKIE else {}
    if requests is not None:
        try:
            r = requests.request(method, url, data=body or None, timeout=30,
                                 allow_redirects=False, headers=hdr)
            text = r.text[: config.OUTPUT_TRUNC]
            hdrs = "\n".join(f"{k}: {v}" for k, v in r.headers.items())
            return f"HTTP {r.status_code}\n{hdrs}\n\n{text}"
        except Exception as e:
            return f"[request failed: {e}]"
    # Fallback without the requests library.
    import urllib.request
    try:
        req = urllib.request.Request(url, method=method, headers=hdr,
                                     data=(body.encode() if body else None))
        with urllib.request.urlopen(req, timeout=30) as resp:
            return f"HTTP {resp.status}\n\n{resp.read(config.OUTPUT_TRUNC).decode(errors='replace')}"
    except Exception as e:
        return f"[request failed: {e}]"


def sql_injection_test(path: str, param: str, method: str = "GET") -> str:
    """Run sqlmap against one parameter on one in-scope path."""
    if not _PATH_RE.match(path):
        return "Invalid path."
    if not _PARAM_RE.match(param):
        return "Invalid param name."
    url = scope.target_url(path)  # validates scope
    argv = ["sqlmap", "-u", url, "-p", param, "--batch",
            "--level=2", "--risk=1", "--flush-session"]
    if config.TARGET_COOKIE:
        argv += [f"--cookie={config.TARGET_COOKIE}"]
    if method.upper() == "POST":
        argv += ["--data", f"{param}=1", "--method=POST"]
    return _run(argv)


def note_finding(title: str, severity: str, description: str,
                 evidence: str = "", repro_steps: str = "") -> str:
    """Record a confirmed finding for the final report."""
    sev = severity.lower()
    if sev not in {"info", "low", "medium", "high", "critical"}:
        sev = "info"
    FINDINGS.add(title, sev, description, evidence, repro_steps)
    return f"Recorded finding: [{sev.upper()}] {title} (total: {len(FINDINGS)})"


def generate_report() -> str:
    """Write the pen-test report from everything recorded so far."""
    path = FINDINGS.save()
    return f"Report written to {path} with {len(FINDINGS)} finding(s)."


# ---- schemas the model sees -------------------------------------------------

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "port_scan",
        "description": "nmap service/version scan of the in-scope target host.",
        "parameters": {"type": "object", "properties": {
            "ports": {"type": "string",
                      "description": "'top1000' or a list like '80,443,8080'."}}},
    }},
    {"type": "function", "function": {
        "name": "web_fingerprint",
        "description": "Identify the target's web server, framework and tech.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "content_discovery",
        "description": "Brute-force directories/files on the target (ffuf).",
        "parameters": {"type": "object", "properties": {
            "wordlist": {"type": "string", "enum": ["common"]}}},
    }},
    {"type": "function", "function": {
        "name": "http_request",
        "description": "Send one HTTP request to a path on the target.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "e.g. '/login'"},
            "method": {"type": "string"},
            "body": {"type": "string"}},
            "required": ["path"]},
    }},
    {"type": "function", "function": {
        "name": "sql_injection_test",
        "description": "Test one parameter on one path for SQL injection (sqlmap).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "param": {"type": "string"},
            "method": {"type": "string"}},
            "required": ["path", "param"]},
    }},
    {"type": "function", "function": {
        "name": "note_finding",
        "description": "Record a confirmed vulnerability for the report.",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"},
            "severity": {"type": "string",
                         "enum": ["info", "low", "medium", "high", "critical"]},
            "description": {"type": "string"},
            "evidence": {"type": "string"},
            "repro_steps": {"type": "string",
                            "description": "Numbered steps to reproduce."}},
            "required": ["title", "severity", "description"]},
    }},
    {"type": "function", "function": {
        "name": "generate_report",
        "description": "Compile all recorded findings into the final report. "
                       "Call this once when the assessment is complete.",
        "parameters": {"type": "object", "properties": {}},
    }},
]

DISPATCH = {
    "port_scan": port_scan,
    "web_fingerprint": web_fingerprint,
    "content_discovery": content_discovery,
    "http_request": http_request,
    "sql_injection_test": sql_injection_test,
    "note_finding": note_finding,
    "generate_report": generate_report,
}


def call(name: str, args: dict) -> str:
    """Execute a tool by name, converting any scope error into a message the
    model can read and react to (rather than crashing the loop)."""
    fn = DISPATCH.get(name)
    if fn is None:
        return f"[unknown tool: {name}]"
    try:
        return fn(**args)
    except scope.OutOfScope as e:
        return f"[BLOCKED] {e}"
    except TypeError as e:
        return f"[bad arguments for {name}: {e}]"
