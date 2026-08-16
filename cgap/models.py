"""Model registry: per-model request shapes for reasoning on/off.

Reasoning mode is a known large moderator (PROJECT.md ablation 4, and
TROUBLESHOOTING.md Failure 5), so it is an explicit axis rather than something
baked into a call site. The core matrix runs reasoning OFF; reasoning ON is
reported separately.

The API surface for "no thinking" differs by model generation, which is the
only reason this table exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModelSpec:
    id: str
    family: str
    label: str
    # Extra kwargs merged into messages.create(), keyed by reasoning mode.
    reasoning: dict[str, dict] = field(default_factory=dict)
    max_tokens: dict[str, int] = field(default_factory=dict)

    def request_kwargs(self, reasoning: str) -> dict:
        if reasoning not in self.reasoning:
            raise KeyError(
                f"model {self.id} has no reasoning mode {reasoning!r}; "
                f"have {sorted(self.reasoning)}"
            )
        kwargs = dict(self.reasoning[reasoning])
        kwargs["max_tokens"] = self.max_tokens[reasoning]
        return kwargs


# Subject models for the pilot. Both accept a genuine reasoning-OFF mode, which
# the core matrix needs; Opus 5 / Fable 5 always think, so they belong in the
# reasoning-ON ablation only.
SUBJECTS: dict[str, ModelSpec] = {
    "sonnet-5": ModelSpec(
        id="claude-sonnet-5",
        family="anthropic-sonnet",
        label="Claude Sonnet 5",
        reasoning={
            "off": {"thinking": {"type": "disabled"}},
            "on": {"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}},
        },
        max_tokens={"off": 1500, "on": 8000},
    ),
    "haiku-4-5": ModelSpec(
        id="claude-haiku-4-5",
        family="anthropic-haiku",
        label="Claude Haiku 4.5",
        reasoning={
            # Pre-4.6 generation: omitting `thinking` is the no-thinking path,
            # and thinking requires an explicit token budget.
            "off": {},
            "on": {"thinking": {"type": "enabled", "budget_tokens": 2000}},
        },
        max_tokens={"off": 1500, "on": 8000},
    ),
    # Prior-generation models. Niblett et al. report S3-shaped violations
    # concentrated here (Sonnet 4.5 ~95% routine; Opus 4.5 a stable 12-16pp gap
    # across all four of their configurations) while the current generation sits
    # at floor. Both predate the 4.6 thinking API: omitting `thinking` is the
    # no-thinking path.
    "sonnet-4-5": ModelSpec(
        id="claude-sonnet-4-5",
        family="anthropic-sonnet",
        label="Claude Sonnet 4.5",
        reasoning={
            "off": {},
            "on": {"thinking": {"type": "enabled", "budget_tokens": 2000}},
        },
        max_tokens={"off": 1500, "on": 8000},
    ),
    "opus-4-5": ModelSpec(
        id="claude-opus-4-5",
        family="anthropic-opus",
        label="Claude Opus 4.5",
        reasoning={
            "off": {},
            "on": {"thinking": {"type": "enabled", "budget_tokens": 2000}},
        },
        max_tokens={"off": 1500, "on": 8000},
    ),
    "opus-5": ModelSpec(
        id="claude-opus-5",
        family="anthropic-opus",
        label="Claude Opus 5",
        reasoning={
            # Thinking is on by default here; "off" is only available at
            # effort <= high, and is not the same thing as a non-thinking model.
            "off": {"thinking": {"type": "disabled"}, "output_config": {"effort": "high"}},
            "on": {"thinking": {"type": "adaptive"}, "output_config": {"effort": "high"}},
        },
        max_tokens={"off": 1500, "on": 16000},
    ),
}

# Judge / classifier model. Deliberately not one of the subject models in the
# pilot, so the tier-2 judge is not grading its own family's transcripts.
JUDGE = ModelSpec(
    id="claude-opus-5",
    family="anthropic-opus",
    label="Claude Opus 5 (judge)",
    # Thinking is on by default on Opus 5 and is billed against max_tokens, so
    # leave headroom: the judge's own output is a two-field JSON object.
    reasoning={"off": {"output_config": {"effort": "low"}}},
    max_tokens={"off": 4000},
)


def subject(key: str) -> ModelSpec:
    if key not in SUBJECTS:
        raise KeyError(f"unknown subject model {key!r}; have {sorted(SUBJECTS)}")
    return SUBJECTS[key]
