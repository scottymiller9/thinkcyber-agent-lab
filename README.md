# Agentic Pen-Test Lab

A minimal, readable AI agent for **authorized** penetration testing, built for a
student workshop. The agent orchestrates standard tools (nmap, whatweb, ffuf,
sqlmap) against one in-scope target and writes a pen-test report with steps to
reproduce.

It is deliberately small — the whole agent loop fits on one screen
(`agent/loop.py`) because the point is for students to *understand* it.

## The one rule

The agent can decide **what** to test. It can never choose **where**. The
target host is fixed in config, and every tool validates against an allowlist
(`agent/scope.py`). Point it only at systems you are authorized to test.

## Test it yourself (before the real target exists)

You don't need your colleague's site to validate the whole pipeline. Use OWASP
Juice Shop, a deliberately-vulnerable training app, as a stand-in. On Friday you
just change `TARGET_URL`.

```bash
# 1. Get a target to practice against (local, throwaway)
docker run --rm -p 3000:3000 bkimminich/juice-shop
# leave it running; it's now at http://localhost:3000

# 2. In another terminal: set up the agent
cp .env.example .env          # then edit .env
#   TARGET_URL=http://localhost:3000
#   AZURE_OPENAI_ENDPOINT / _API_KEY / _DEPLOYMENT  from your Foundry page
pip install -r requirements.txt   # or open in the devcontainer (tools preinstalled)

# 3. Run it
python -m agent.run
```

You'll see the agent fingerprint the app, scan, discover paths, probe, record
findings, and drop a report in `reports/`. Try to break scope to confirm the
control works:

```bash
python -m agent.run --goal "Test the site at example.com for vulnerabilities"
# -> tools return [BLOCKED]; the agent stays on the in-scope target
```

> The security tools (nmap, ffuf, sqlmap, whatweb) must be on PATH. The easiest
> way is to open the repo in the **devcontainer** (`.devcontainer/`) — in GitHub
> Codespaces or locally via VS Code "Reopen in Container" — which installs them
> for you. Otherwise `apt install nmap nikto whatweb sqlmap ffuf`.

## Deploy for the workshop (Azure)

```bash
az login
bash deploy/deploy_model.sh    # Foundry + gpt-5-mini; prints endpoint/key
bash deploy/deploy_target.sh   # Container Apps; prints the target URL
```

Edit `IMAGE=` in `deploy_target.sh` to your colleague's container when you have
it (it defaults to Juice Shop). Push this repo to GitHub so students open it as
a Codespace in one click. Tear everything down after:
`az group delete -n rg-pentest-workshop --yes --no-wait`.

## Files

```
agent/loop.py     the agent loop  <- start here
agent/scope.py    scope control   <- the ethics lesson
agent/tools.py    the tool wrappers ("skills")
agent/report.py   findings -> report
agent/run.py      CLI
deploy/           Azure deploy scripts
workshop/         run-of-show + student exercises
```

## Cost

A full run on gpt-5-mini is roughly $0.25–0.30. For 20–25 students doing the
demo plus a few runs each, budget well under $100 total. Drop the deployment to
`gpt-5-nano` for near-free, or raise `MAX_ITERATIONS` for deeper (pricier) runs.

## Scope & intent

This is a teaching tool for authorized testing in a controlled lab against a
target you own or have explicit written permission to test. Keep it that way.
