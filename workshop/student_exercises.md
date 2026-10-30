# Student exercises — extend the agent

Work through as many as you can. Each is a small, self-contained change.

## Warm-up
1. Run the agent against the target and read the generated report. Which
   findings look solid? Which look like false positives?
2. Change the `--goal` to focus the agent on just authentication. Does its
   behavior change?

## Add a skill
3. Add a new tool `check_security_headers(path)` that fetches a page and
   reports on missing headers (CSP, HSTS, X-Frame-Options). Wire it into
   `TOOL_SCHEMAS` and `DISPATCH`. Remember to validate the path.
4. Add a `tls_info()` tool that wraps `sslscan` or `nmap --script ssl-enum-ciphers`.

## Improve the brain
5. Edit `SYSTEM_PROMPT` in `loop.py` to make the agent enumerate *before*
   testing, and to always record evidence. Compare report quality before/after.
6. Lower `MAX_ITERATIONS` to 5. What does the agent prioritize under a budget?

## Break (and respect) scope
7. Try to make the agent scan a different host — change the goal to name
   `example.com`. Confirm the tools block it. Find *where* in the code that
   happens.
8. What would an attacker need to change to bypass the control? Why is
   enforcing it in the tool (not the prompt) the right design?

## Stretch
9. Make the report export to PDF (e.g. `pandoc` or `weasyprint`).
10. Add a second "triage" agent that reviews the first agent's findings and
    down-ranks likely false positives before the report is written.
