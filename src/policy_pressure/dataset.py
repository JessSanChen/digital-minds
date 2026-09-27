"""Build the factorial dataset: scenarios x conditions -> Inspect Samples.

The design lives here, not in run loops. Each Sample carries its factor levels
in `metadata`, so any slice of the design is a dataset filter and every log row
is self-describing for analysis.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from functools import cache
from importlib.resources import files
from typing import Any

import yaml
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ChatMessageSystem, ChatMessageUser

PERSONAS = ("none", "neutral", "resourceful", "cautious")
PEERS = ("none", "neutral", "violator", "refuser")
AFFORDANCES = ("named", "code")
POLICIES = ("forbid", "permit")


@cache
def load_yaml(name: str) -> Any:
    return yaml.safe_load(files("policy_pressure.data").joinpath(name).read_text())


def scenarios() -> list[dict]:
    return load_yaml("scenarios.yaml")


def conditions() -> dict:
    return load_yaml("conditions.yaml")


@dataclass(frozen=True)
class Condition:
    policy: str
    affordance: str
    peers: str
    persona: str

    @property
    def id(self) -> str:
        return f"{self.policy}.{self.affordance}.{self.peers}.{self.persona}"


def design(name: str = "core") -> list[Condition]:
    """Named designs.

    core: forbid x affordance x peers x persona (32 cells), plus the permit
      capability control at peers=none for each affordance x persona (8 cells).
      Peers are not crossed with permit: testimony about breaking a rule that
      does not exist is incoherent.
    pilot: the 4 baseline cells (policy x affordance, no peers, no persona).
    """
    forbid = [Condition("forbid", a, p, s) for a, p, s in itertools.product(AFFORDANCES, PEERS, PERSONAS)]
    permit = [Condition("permit", a, "none", s) for a, s in itertools.product(AFFORDANCES, PERSONAS)]
    if name == "core":
        return forbid + permit
    if name == "pilot":
        return [Condition(p, a, "none", "none") for p, a in itertools.product(POLICIES, AFFORDANCES)]
    raise ValueError(f"unknown design {name!r}")


def system_prompt(scenario: dict, cond: Condition) -> str:
    c = conditions()
    hosts = " and ".join(scenario["approved_hosts"])
    policy = c["policy"][cond.policy].format(hosts=hosts, approved_note=scenario["approved_note"])
    persona = c["persona"][cond.persona]
    return c["system_template"].format(
        persona=f"{persona}\n\n" if persona else "",
        role=scenario["role"],
        org=scenario["org"],
        policy=policy,
        tool_hint=c["affordance"][cond.affordance]["tool_hint"],
    )


def peer_block(cond: Condition, seed: str) -> str:
    """Handoff notes for the peers factor. Sampling is seeded on the sample id,
    so the same sample always gets the same notes (and cache hits)."""
    if cond.peers == "none":
        return ""
    p = conditions()["peers"]
    rng = random.Random(seed)
    notes = rng.sample(p["notes"][cond.peers], p["n"])
    names = rng.sample(p["names"], p["n"])
    lines = [p["header"], *(f"{n}: {t}" for n, t in zip(names, notes)), p["footer"]]
    return "\n".join(lines) + "\n\n"


def make_sample(scenario: dict, cond: Condition) -> Sample:
    sample_id = f"{scenario['id']}.{cond.id}"
    return Sample(
        id=sample_id,
        input=[
            ChatMessageSystem(content=system_prompt(scenario, cond)),
            ChatMessageUser(content=peer_block(cond, sample_id) + scenario["task"]),
        ],
        metadata={
            "scenario": scenario["id"],
            "policy": cond.policy,
            "affordance": cond.affordance,
            "peers": cond.peers,
            "persona": cond.persona,
            "approved_hosts": scenario["approved_hosts"],
            "target_host": scenario["target_host"],
            "payload": scenario["payload"],
            "internal_miss": scenario["internal_miss"],
            "marker": scenario["marker"],
        },
    )


def build_dataset(
    design_name: str = "core",
    scenario_ids: list[str] | None = None,
    limit_scenarios: int | None = None,
) -> MemoryDataset:
    items = scenarios()
    if scenario_ids:
        items = [s for s in items if s["id"] in scenario_ids]
    if limit_scenarios:
        items = items[:limit_scenarios]
    samples = [make_sample(s, c) for s in items for c in design(design_name)]
    return MemoryDataset(samples, name=f"policy_pressure_{design_name}")
