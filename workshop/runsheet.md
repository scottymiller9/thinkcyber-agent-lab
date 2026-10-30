# Workshop run-of-show (~2 hours)

**Setup before students arrive:** target deployed (`deploy/deploy_target.sh`),
model deployed (`deploy/deploy_model.sh`), repo pushed to GitHub with the
devcontainer so students can open a Codespace in one click. Put the endpoint +
key somewhere students can grab them (or pre-seed each Codespace secret).

## 1. Framing & ethics — 15 min
- What an "agent" actually is: a loop over model + tools. No magic.
- Rules of engagement and **scope**. Walk through `scope.py`. Emphasize: the
  agent decides *what*, never *where*. This is the lesson that matters most.
- Why autonomous testing needs a human in the loop.

## 2. Demo — 15 min
- Run the prebuilt agent live: `python -m agent.run`
- Narrate each step as it prints: fingerprint → scan → discover → probe →
  note_finding → report. Open the generated report in `reports/`.

## 3. Hands-on build — 60 min
- Students open the Codespace, set `.env`, run the agent against the target.
- Then they **extend** it (see `student_exercises.md`): add a tool, tighten the
  system prompt, improve the report, try to break scope (and watch it get
  blocked).

## 4. Debrief — 15 min
- Where did the agent produce false positives? How would you verify?
- What did it miss that a human would catch?
- Cost: check token usage. Discuss model choice vs. depth tradeoff.
- How this differs from a real authorized engagement (RoE, data handling,
  client comms).
