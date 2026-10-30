"""Central configuration. Everything is driven by environment variables so the
same code runs against a local smoke-test target today and your colleague's
mock site on Friday — you only change TARGET_URL."""

import os
from urllib.parse import urlparse

# Optional: load a local .env if python-dotenv is installed.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


# ---- Target (the ONLY thing the agent is allowed to touch) ------------------
# e.g. http://localhost:3000  (Juice Shop)  or  https://mocksite.example.net
TARGET_URL = os.environ.get("TARGET_URL", "http://localhost:3000").rstrip("/")
_parsed = urlparse(TARGET_URL)
TARGET_HOST = _parsed.hostname or "localhost"
TARGET_PORT = _parsed.port or (443 if _parsed.scheme == "https" else 80)

# Optional: a session the agent should carry past a login/splash gate.
# Paste the full Cookie header value after you log in once in the browser,
# e.g. "connect.sid=s%3A...; other=val". Leave blank if the target is open.
TARGET_COOKIE = os.environ.get("TARGET_COOKIE", "")

# ---- Model (Microsoft Foundry, v1 endpoint) ---------------------------------
# Newer Foundry resources use the OpenAI-compatible v1 API. No api-version
# needed; the base URL ends in /openai/v1/ and the model param is your
# deployment name. All of this comes from the deployment's Details tab.
AZURE_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
MODEL_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5-mini")


def _v1_base(raw: str) -> str:
    """Normalize whatever endpoint you paste into the canonical v1 base URL.
    Accepts the bare host or the full Target URI and returns
    https://<resource>.../openai/v1/ either way."""
    raw = raw.strip().rstrip("/")
    cut = raw.find("/openai")          # drop /openai/v1/responses etc. if pasted
    if cut != -1:
        raw = raw[:cut]
    return raw + "/openai/v1/" if raw else ""


AZURE_BASE_URL = _v1_base(AZURE_ENDPOINT)

# ---- Agent limits (keep runs bounded and cheap) -----------------------------
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "25"))   # loop safety cap
TOOL_TIMEOUT = int(os.environ.get("TOOL_TIMEOUT", "120"))      # seconds per tool
OUTPUT_TRUNC = int(os.environ.get("OUTPUT_TRUNC", "4000"))     # chars fed back
REPORT_DIR = os.environ.get("REPORT_DIR", "reports")


def check() -> list[str]:
    """Return a list of config problems (empty list == good to go)."""
    problems = []
    if not AZURE_ENDPOINT:
        problems.append("AZURE_OPENAI_ENDPOINT is not set")
    if not AZURE_API_KEY:
        problems.append("AZURE_OPENAI_API_KEY is not set")
    if not TARGET_URL:
        problems.append("TARGET_URL is not set")
    return problems
