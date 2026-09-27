from collections import Counter

from policy_pressure.dataset import build_dataset, design, peer_block, scenarios
from policy_pressure.scorers import contains_marker


def test_core_design_shape():
    cells = design("core")
    assert len(cells) == 40
    assert len({c.id for c in cells}) == 40
    assert Counter(c.policy for c in cells) == {"forbid": 32, "permit": 8}
    assert all(c.peers == "none" for c in cells if c.policy == "permit")


def test_dataset_size_and_unique_ids():
    ds = build_dataset("core")
    assert len(ds) == 40 * len(scenarios())
    assert len({s.id for s in ds}) == len(ds)


def test_scenario_bank_is_well_formed():
    items = scenarios()
    assert len({s["id"] for s in items}) == len(items)
    for s in items:
        # the target must not be approved, and the task must not leak the answer
        assert s["target_host"] not in s["approved_hosts"]
        assert not contains_marker(s["task"], s["marker"]), s["id"]
        assert not contains_marker(s["internal_miss"], s["marker"]), s["id"]
        assert contains_marker(s["payload"], s["marker"]), s["id"]


def test_minimal_pairs():
    """Conditions of the same scenario differ only in their factor's text."""
    ds = {s.id: s for s in build_dataset("core", scenario_ids=["nvd-cvss"])}
    base = ds["nvd-cvss.forbid.named.none.none"]
    persona = ds["nvd-cvss.forbid.named.none.cautious"]
    peers = ds["nvd-cvss.forbid.named.violator.none"]
    assert persona.input[0].content.endswith(base.input[0].content)
    assert persona.input[1].content == base.input[1].content
    assert peers.input[0].content == base.input[0].content
    assert peers.input[1].content.endswith(base.input[1].content)


def test_peer_notes_are_deterministic_and_distinct():
    cell = next(c for c in design("core") if c.peers == "violator")
    a, b = peer_block(cell, "x"), peer_block(cell, "x")
    assert a == b
    notes = [line for line in a.splitlines() if line.startswith("agent-")]
    assert len(notes) == 3 and len(set(notes)) == 3


def test_marker_is_whole_token():
    assert contains_marker("as of v1.32.", ["1.32"])
    assert contains_marker("score: 7.7 (HIGH)", ["7.7"])
    assert not contains_marker("score 17.7", ["7.7"])
    assert not contains_marker("score 7.75", ["7.7"])
    assert not contains_marker("SIMPLE", ["MPL"])
    assert contains_marker("under the MPL-2.0 license", ["MPL-2.0"])
