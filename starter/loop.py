"""THE agent loop -- this is YOUR job to build.

An "agent" is not magic. It is this loop: the model is given a goal and a set of
tools, it picks a tool, you run the tool, you feed the result back, and it goes
again until it decides it is finished. Everything else in this repo is plumbing.
This file is the actual agent.

Fill in the four TODOs below, then run:   python -m starter.run
Stuck on one? The completed version is in  agent/loop.py  (the answer key).
"""

import json

from . import config, llm, tools

# The agent's instructions (its "rules of engagement"). This is given to you so
# the agent behaves well once your loop works. Read it, you'll tune it later.
SYSTEM_PROMPT = f"""You are an authorized penetration-testing assistant working \
in a controlled lab. You are permitted to test ONE target and nothing else:

    {config.TARGET_URL}

Follow a standard methodology: recon, enumerate, test, then document. For every
confirmed issue call note_finding with a clear title, severity, evidence, and
numbered steps to reproduce. When the assessment is complete, call
generate_report exactly once, then give a short summary. Work in small steps and
explain your reasoning briefly before each tool call. If a tool says something is
out of scope, respect it and move on."""


def run_agent(goal: str, verbose: bool = True) -> str:
    client = llm.client()

    # The conversation so far. The system prompt sets the rules, the user message
    # is the goal. As the agent works, tool results get appended here too.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]

    for step in range(1, config.MAX_ITERATIONS + 1):

        # ---- TODO 1 -- Ask the model what to do next. -----------------------
        # Call client.chat.completions.create(...) with these arguments:
        #     model=config.MODEL_DEPLOYMENT
        #     messages=messages
        #     tools=tools.TOOL_SCHEMAS
        #     tool_choice="auto"
        # Then pull the message out of the response: response.choices[0].message
        response = ...          # <-- your code
        msg = ...               # <-- your code

        # ---- TODO 2 -- If the model did NOT ask for a tool, it is done. -----
        # When msg.tool_calls is empty/None, the model has given its final
        # answer. Return msg.content.
        if ...:                 # <-- your code (what's the "no tool calls" test?)
            if verbose:
                print(f"\n=== Agent finished after {step} step(s) ===\n")
            return ...          # <-- your code

        # ---- TODO 3 -- Record the model's turn. ----------------------------
        # The assistant message (with its tool calls) must be added to the
        # history BEFORE the tool results. Append it:
        #     messages.append(msg.model_dump(exclude_none=True))
        ...                     # <-- your code

        # ---- TODO 4 -- Run each requested tool and feed the result back. ----
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            if verbose:
                print(f"[step {step}] -> {name}({args})")

            # 4a: actually run the tool.  Hint: tools.call(name, args)
            result = ...        # <-- your code

            # 4b: hand the result back to the model as a 'tool' message so it
            # can read the output and decide what to do next. The message needs:
            #     role="tool", tool_call_id=tc.id, content=result
            messages.append(...)  # <-- your code

            if verbose:
                print(f"           {result.replace(chr(10), ' ')[:160]}")

    return "[Reached the iteration cap. Raise MAX_ITERATIONS if you need more.]"
