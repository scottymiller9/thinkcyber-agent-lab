"""THE agent loop.

This is the part the workshop is really about. An "agent" is not magic — it is
this loop: give the model a goal and a set of tools, let it pick a tool, run
the tool, feed the result back, and repeat until it's done. Read it top to
bottom; it fits on one screen.
"""

import json

from . import config, llm, tools

# Rules of engagement. This frames the model's behavior and (together with the
# scope control in scope.py) keeps it methodical and on-target.
SYSTEM_PROMPT = f"""You are an authorized penetration-testing assistant working \
in a controlled lab. You are permitted to test ONE target and nothing else:

    {config.TARGET_URL}

Follow a standard methodology:
  1. Recon  - fingerprint the web stack and scan for open services.
  2. Enumerate - discover paths, endpoints, and parameters.
  3. Test - probe for common web vulnerabilities (injection, auth issues,
     misconfig, exposed data). Use the provided tools; do not fabricate results.
  4. Document - for every confirmed issue call note_finding with a clear
     title, severity, evidence, and numbered steps to reproduce.

When the assessment is complete, call generate_report exactly once, then give a
short summary to the user. Work in small steps and explain your reasoning
briefly before each tool call. If a tool reports something is out of scope or
blocked, respect it and move on."""


def run_agent(goal: str, verbose: bool = True) -> str:
    client = llm.client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]

    for step in range(1, config.MAX_ITERATIONS + 1):
        response = client.chat.completions.create(
            model=config.MODEL_DEPLOYMENT,
            messages=messages,
            tools=tools.TOOL_SCHEMAS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        # No tool calls -> the model is done and this is its final answer.
        if not msg.tool_calls:
            if verbose:
                print(f"\n=== Agent finished after {step} step(s) ===\n")
            return msg.content or ""

        # Record the assistant's turn (it must precede the tool results).
        messages.append(msg.model_dump(exclude_none=True))

        # Execute each requested tool and feed the result back.
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            if verbose:
                print(f"[step {step}] -> {name}({args})")
            result = tools.call(name, args)
            if verbose:
                preview = result.replace("\n", " ")[:160]
                print(f"           {preview}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return "[Reached the iteration cap. Increase MAX_ITERATIONS if needed.]"
