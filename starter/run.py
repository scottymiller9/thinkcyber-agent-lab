"""CLI entrypoint.  Usage:  python -m agent.run  [--goal "..."]"""

import argparse
import sys

from . import config, scope
from .loop import run_agent

DEFAULT_GOAL = (
    "Perform a web application penetration test of the target. Find and "
    "document as many issues as you can, then produce the report."
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Agentic pen-test lab")
    ap.add_argument("--goal", default=DEFAULT_GOAL, help="what to ask the agent to do")
    ap.add_argument("--quiet", action="store_true", help="suppress step-by-step output")
    args = ap.parse_args()

    problems = config.check()
    if problems:
        print("Configuration problems:")
        for p in problems:
            print("  -", p)
        print("\nCopy .env.example to .env and fill it in (or export the vars).")
        return 1

    print(f"Target in scope: {sorted(scope.ALLOWED_HOSTS)}  ({config.TARGET_URL})")
    print(f"Model: {config.MODEL_DEPLOYMENT}\n")

    final = run_agent(args.goal, verbose=not args.quiet)
    print("\n--- Agent summary ---\n")
    print(final)
    return 0


if __name__ == "__main__":
    sys.exit(main())
