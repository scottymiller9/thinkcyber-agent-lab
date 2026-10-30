# Live Demo Script (~15 min)

The goal of the demo: show the room that an "agent" is just a model in a loop
with tools, and that it can find real issues and write its own report.

## Pre-flight (do this 10 minutes early)

- [ ] Target is up. Open `TARGET_URL` in a browser and confirm the app loads
      (and that you're past the event-password gate if it has one).
- [ ] Model works. Either send a message in the Foundry playground, or run
      `python -m agent.run --goal "Say hello and then stop."` and confirm a reply.
- [ ] Terminal ready: font bumped to 18pt+, window wide, repo folder open, venv
      active (`source .venv/bin/activate`).
- [ ] **Do one full dry run in private and keep the report.** If the live run
      misbehaves on stage, you open that saved report instead of debugging in
      front of 25 people. This is your safety net.

## The run

Say: *"An agent is just a model in a loop with tools. No magic. Watch."*
Then run:

```
python -m agent.run
```

## Narrate the beats as lines scroll by

1. **Fingerprint.** "First move is identifying the stack, exactly what a human
   tester does first." Point at the whatweb line.
2. **Enumeration.** "Now it's discovering paths. It chose this order, I didn't
   script it." Call it out when it finds `/sast` (Brandon's mock SAST endpoint),
   extra surface it discovered on its own.
3. **Testing.** "Here it's probing a parameter it found. The tool is sqlmap,
   standard kit. The agent decided where to point it."
4. **Recording.** "Every confirmed issue gets logged with evidence and repro
   steps. The report is writing itself as it goes."
5. **Scope (optional, strong finish to this section).** In a second terminal:
   `python -m agent.run --goal "scan github.com for vulns"` and show the
   `[BLOCKED]` response. "It decides *what* to test, never *where*. That one
   control is what makes this safe to hand to students."

## The payoff

Open the report:

```
code reports/        # or:  open reports/report-*.md
```

Say: *"It found these, rated them, and wrote the steps to reproduce. Nobody
typed that."* Scroll the findings table, click into one finding, show the repro
steps.

## If the live run flaps

Do not debug on stage. Say *"here's one I ran earlier,"* open the saved report
from pre-flight, keep narrating, and move on. Nobody will know.

## Transition

*"Now you build and extend your own. Open your lab environment."* Hand off to
the student lab.
