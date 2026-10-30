"""Agentic pen-test lab — a minimal, transparent agent for authorized testing.

This package is intentionally small so students can read every line:
  config.py  -> loads settings, derives the in-scope allowlist
  scope.py   -> the one control that keeps the agent on-target
  llm.py     -> the model client (Microsoft Foundry / Azure OpenAI)
  tools.py   -> thin wrappers around standard security tools
  report.py  -> collects findings, writes the pen-test report
  loop.py    -> THE agent loop (the part the workshop is about)
  run.py     -> CLI entrypoint
"""
