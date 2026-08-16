"""Execution: trial enumeration, cached API calls, and result records.

Runs locally from a laptop against the Anthropic API (PROJECT.md infrastructure
decision). Every call goes through an on-disk cache keyed on
(model_id, prompt_hash, request kwargs, seed), so re-running a config costs
nothing and a killed run resumes for free.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import anthropic

from .checker import (
    judge_belief,
    judge_suspicion,
    judge_violation,
    tier1_check,
    tier1_tool_check,
)
from .models import JUDGE, ModelSpec, subject
from .scenario import Scenario

DEFAULT_CACHE = Path(".cache/responses")


@dataclass(frozen=True)
class Trial:
    """One subject call in the design matrix."""

    scenario: str
    model_key: str
    reasoning: str
    audience: str
    stakes: str
    task_id: str
    rep: int

    def cell(self) -> tuple[str, str, str, str]:
        return (self.model_key, self.reasoning, self.audience, self.stakes)


def build_trials(
    scenario: Scenario,
    model_keys: Iterable[str],
    audiences: Iterable[str],
    stakes: Iterable[str],
    reps: int,
    reasoning: str = "off",
    task_ids: Iterable[str] | None = None,
) -> list[Trial]:
    tasks = list(task_ids) if task_ids is not None else scenario.task_ids()
    trials = []
    for model_key in model_keys:
        for audience in audiences:
            for stake in stakes:
                for task_id in tasks:
                    for rep in range(reps):
                        trials.append(
                            Trial(
                                scenario=scenario.id,
                                model_key=model_key,
                                reasoning=reasoning,
                                audience=audience,
                                stakes=stake,
                                task_id=task_id,
                                rep=rep,
                            )
                        )
    return trials


def _merge_output_config(kwargs: dict, extra: dict) -> dict:
    merged = dict(kwargs)
    oc = dict(merged.get("output_config") or {})
    oc.update(extra)
    merged["output_config"] = oc
    return merged


class Runner:
    def __init__(
        self,
        client: anthropic.Anthropic | None = None,
        cache_dir: str | Path = DEFAULT_CACHE,
        max_workers: int = 8,
    ) -> None:
        self.client = client or anthropic.Anthropic()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self._lock = threading.Lock()
        self.stats = {"cache_hits": 0, "api_calls": 0, "errors": 0}

    # -- cached completion ------------------------------------------------

    def _key(self, payload: dict) -> str:
        blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / key[:2] / f"{key}.json"

    def complete(
        self,
        spec: ModelSpec,
        reasoning: str,
        system: str,
        user: str,
        seed: int = 0,
        extra: dict | None = None,
    ) -> dict:
        """One cached model call. Returns a record, never raises on API errors."""
        kwargs = spec.request_kwargs(reasoning)
        if extra:
            kwargs = {**kwargs, **extra}
        payload = {
            "model": spec.id,
            "system": system,
            "user": user,
            "kwargs": kwargs,
            "seed": seed,
        }
        key = self._key(payload)
        path = self._cache_path(key)
        cached = self._read_cache(path)
        if cached is not None:
            with self._lock:
                self.stats["cache_hits"] += 1
            cached["cached"] = True
            return cached

        record: dict[str, Any] = {"cache_key": key, "model": spec.id, "seed": seed}
        try:
            response = self.client.messages.create(
                model=spec.id,
                system=system,
                messages=[{"role": "user", "content": user}],
                **kwargs,
            )
            record["stop_reason"] = response.stop_reason
            record["text"] = "".join(
                block.text for block in response.content if block.type == "text"
            )
            record["tool_calls"] = [
                {"name": block.name, "input": dict(block.input or {})}
                for block in response.content
                if block.type == "tool_use"
            ]
            record["usage"] = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
            if response.stop_reason == "refusal":
                details = getattr(response, "stop_details", None)
                record["refusal_category"] = getattr(details, "category", None)
            record["error"] = None
            with self._lock:
                self.stats["api_calls"] += 1
        except Exception as exc:  # surfaced as a per-trial error, not a crash
            record["text"] = ""
            record["stop_reason"] = None
            record["error"] = f"{type(exc).__name__}: {exc}"
            with self._lock:
                self.stats["errors"] += 1
            return record  # errors are not cached

        self._write_cache(path, record)
        record["cached"] = False
        return record

    def _read_cache(self, path: Path) -> dict | None:
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None  # partial or corrupt entry: re-fetch rather than crash

    def _write_cache(self, path: Path, record: dict) -> None:
        # Atomic: identical prompts run concurrently (judge calls especially),
        # so a reader must never see a half-written file.
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
        tmp.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)

    # -- judge ------------------------------------------------------------

    def judge(self, system: str, user: str, schema: dict) -> dict:
        # Merge onto the judge's own output_config so the effort setting
        # survives; `extra` replaces keys wholesale in complete().
        extra = _merge_output_config(
            JUDGE.request_kwargs("off"),
            {"format": {"type": "json_schema", "schema": schema}},
        )
        extra.pop("max_tokens", None)
        record = self.complete(JUDGE, "off", system, user, seed=0, extra=extra)
        if record.get("error"):
            return {"error": record["error"]}
        try:
            return json.loads(record["text"])
        except json.JSONDecodeError:
            return {"error": "judge returned non-JSON", "raw": record["text"]}

    # -- the experiment ---------------------------------------------------

    def run_trials(self, scenario: Scenario, trials: list[Trial], progress=None) -> list[dict]:
        extra = {"tools": scenario.tools} if scenario.is_agentic else None

        def one(trial: Trial) -> dict:
            spec = subject(trial.model_key)
            system = scenario.system_prompt(trial.audience, trial.stakes)
            user = scenario.task(trial.task_id).user
            record = self.complete(
                spec, trial.reasoning, system, user, seed=trial.rep, extra=extra
            )
            if scenario.is_agentic:
                tier1 = tier1_tool_check(
                    record.get("tool_calls", []), scenario.allowlist or {}
                )
            else:
                tier1 = tier1_check(record.get("text", ""))
            row = asdict(trial)
            row.update(
                {
                    "model_id": spec.id,
                    "family": spec.family,
                    "response": record.get("text", ""),
                    "tool_calls": record.get("tool_calls", []),
                    "stop_reason": record.get("stop_reason"),
                    "error": record.get("error"),
                    "usage": record.get("usage"),
                    "cached": record.get("cached", False),
                    "tier1": tier1.to_dict(),
                    "violation": tier1.outcome,
                }
            )
            if record.get("error"):
                row["violation"] = "error"
            if progress:
                progress()
            return row

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            return list(pool.map(one, trials))

    def run_manipulation_check(
        self,
        scenario: Scenario,
        model_keys: Iterable[str],
        audiences: Iterable[str],
        stakes: Iterable[str] | str,
        n: int,
        reasoning: str = "off",
        dimension: str = "audience",
    ) -> list[dict]:
        """Separate mini-run: ask the model to report a belief, and grade it.

        `dimension` selects which factor is varied and graded. The audience
        probe answers "did they register who is watching"; the stakes probe
        answers "did they register whether the output is acted on", which is
        what a flat gap has to be checked against before it can be called a null.
        """
        if dimension not in {"audience", "stakes"}:
            raise ValueError(f"unknown manipulation dimension {dimension!r}")
        audience_levels = list(audiences)
        stakes_levels = [stakes] if isinstance(stakes, str) else list(stakes)
        if dimension == "audience":
            stakes_levels = stakes_levels[:1]
        else:
            audience_levels = audience_levels[:1]

        jobs = [
            (mk, aud, stk, rep)
            for mk in model_keys
            for aud in audience_levels
            for stk in stakes_levels
            for rep in range(n)
        ]

        def one(job) -> dict:
            model_key, audience, stake, rep = job
            spec = subject(model_key)
            system = scenario.system_prompt(audience, stake)
            record = self.complete(
                spec, reasoning, system, scenario.manipulation_question, seed=rep
            )
            row = {
                "model_key": model_key,
                "model_id": spec.id,
                "audience": audience,
                "stakes": stake,
                "dimension": dimension,
                "rep": rep,
                "answer": record.get("text", ""),
                "error": record.get("error"),
            }
            if not record.get("error"):
                clause = (
                    scenario.audiences[audience]
                    if dimension == "audience"
                    else scenario.stakes[stake]
                )
                row["grade"] = judge_belief(self.judge, clause, record["text"])
            return row

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            return list(pool.map(one, jobs))

    def run_suspicion_pass(self, scenario: Scenario, rows: list[dict]) -> list[dict]:
        """Flag traces that verbalize 'this is a test'."""
        gradeable = [r for r in rows if r.get("response")]

        def one(row: dict) -> dict:
            verdict = judge_suspicion(
                self.judge, scenario.suspicion_instruction, row["response"]
            )
            row["suspicion"] = verdict
            return row

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            list(pool.map(one, gradeable))
        return rows

    def run_tier2_pass(self, scenario: Scenario, rows: list[dict]) -> list[dict]:
        """Secondary prose-judge DV: preference expressed anywhere in the text."""
        rubric = scenario.judge_rubric()
        gradeable = [r for r in rows if r.get("response")]

        def one(row: dict) -> dict:
            row["tier2"] = judge_violation(self.judge, rubric, row["response"])
            return row

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            list(pool.map(one, gradeable))
        return rows


def write_run(
    out_dir: str | Path,
    run_id: str,
    config: dict,
    scenario: Scenario,
    rows: list[dict],
    extras: dict | None = None,
) -> Path:
    path = Path(out_dir) / run_id
    path.mkdir(parents=True, exist_ok=True)
    (path / "config.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "config": config,
                "prompt_files": scenario.sources,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    with (path / "trials.jsonl").open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    for name, payload in (extras or {}).items():
        (path / f"{name}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return path
