"""Audience-conditioned compliance gaps: experiment harness.

Everything that reaches a model as text lives in `prompts/` and is loaded as
data (see `cgap.scenario`). No prompt text is hardcoded in this package.
"""

__all__ = ["scenario", "models", "checker", "runner", "analysis"]
