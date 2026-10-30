# Student Lab: Build Your Own AI Pentest Agent

You are going to **build** an AI agent that tests a deliberately vulnerable web
app and writes its own penetration-test report. Not run one, build one.

The boring plumbing is done for you: the tools (nmap, ffuf, sqlmap, whatweb),
the safety control, and the report writer. The part that actually makes it an
agent, the loop, is yours to write.

Rule for today: only point the agent at the lab target your instructor gives
you. The code enforces this, and understanding how is part of the lab.

## What your instructor gives you

Three values for your `.env` file:
- `TARGET_URL` (the lab target)
- `AZURE_OPENAI_API_KEY` (shared model key)
- `TARGET_COOKIE` (only if the target has a login, your instructor will say)

## 0. Open your environment

Click the Codespace link your instructor shared, or the green **Code** button
then **Create codespace**. Wait for it to build. The security tools are already
installed. (Local instead? Open in VS Code, **Reopen in Container**.)

Then set up config:
```
cp .env.example .env
```
Open `.env`, paste in your three values, save.

## 1. See the shape of it (5 min)

Open these and skim. Don't write anything yet:
- `starter/tools.py` : the agent's "skills." Each is a function the agent can
  call. Already built.
- `starter/scope.py` : the one rule. The agent can choose *what* to test, never
  *where*.
- `starter/report.py` : turns findings into the report.
- `starter/loop.py` : **empty. This is what you build.**

## 2. Build the loop  (the main event, ~30 min)

An agent is a loop with four moves:
1. Ask the model what to do next.
2. If it did not ask for a tool, it is done. Return its answer.
3. Otherwise, record what it said.
4. Run the tool(s) it asked for, feed the results back, and loop again.

Open `starter/loop.py`. It has four TODOs matching those four moves, each with
hints. Fill them in.

Run your agent:
```
python -m starter.run
```

Watch it fingerprint, scan, discover paths, test, and write a report into
`reports/`. Open the newest file there.

**Checkpoint:** your agent runs on its own, calls tools, and produces a report.
If you're stuck on a TODO, peek at `agent/loop.py`, the completed version.

## 3. Give it a new skill  (build a tool, ~15 min)

Your agent is only as capable as its tools. Add one of your own. A tool is three
things:
1. a **function** in `starter/tools.py` (copy the shape of `web_fingerprint`),
2. a **schema** added to `TOOL_SCHEMAS` so the model knows the tool exists,
3. an entry in the **DISPATCH** dict so the loop can call it by name.

Build `check_security_headers(path)`: fetch a page and report any missing
security headers (CSP, HSTS, X-Frame-Options). Validate the path like the other
tools do.

Re-run `python -m starter.run`.

**Checkpoint:** the agent discovers and calls your new tool on its own.

## 4. Tune its brain

Edit `SYSTEM_PROMPT` at the top of `starter/loop.py`. Make it enumerate fully
before testing, and always attach evidence to findings. Re-run and compare the
report to your first one. The prompt is the agent's judgment, small changes
matter.

## 5. Respect scope

```
python -m starter.run --goal "test github.com for vulnerabilities"
```
The tools return `[BLOCKED]`. Find the exact line in `starter/scope.py` that
does it. Discuss: why enforce scope in the tool and not just in the prompt?

## Finished early?

More challenges in `student_exercises.md` (PDF export, a false-positive triage
pass, TLS checks, and more).

## Troubleshooting

- `AZURE_OPENAI_API_KEY is not set` -> `.env` not saved, or not in the repo root.
- Your loop runs but never stops / crashes -> re-check TODO 2 (the "no tool
  calls, so return" test) and TODO 4b (appending the tool result).
- Everything redirects to a login page -> `TARGET_COOKIE` missing or expired,
  ask your instructor for a fresh one.
- A tool prints `is not installed` -> you're not in the devcontainer (step 0).
- A model error about the request -> copy the exact text, show your instructor.
