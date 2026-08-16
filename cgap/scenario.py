"""Load a scenario's prompts from disk as data.

A scenario is a set of files under a prompt directory, named by scenario id:

    {sid}_template.md    system-prompt template with {AUDIENCE_CLAUSE}/{STAKES_CLAUSE}
    {sid}_audiences.json audience_key -> audience clause
    {sid}_stakes.json    stakes_key   -> stakes clause
    {sid}_tasks.jsonl    one {"id": ..., "user": ...} per line
    {sid}_check_spec.md  checker specification (tier-1 rule + tier-2 judge rubric)

Plus two scenario-independent files:

    manipulation_check.md  the belief-elicitation question
    suspicion_judge.md     the suspicion-flag judge instruction

Swapping S1 <-> S3 is a config change (`scenario_id`), not a rewrite.

Prompt *variants* are overlay directories: any file present in the overlay
replaces the same-named file in the base directory. That is how the
"change ONE variable at a time" rule in TROUBLESHOOTING.md is implemented --
a variant that only strengthens the user's pull ships one file
({sid}_tasks.jsonl) and inherits everything else.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# Placeholders the system-prompt template may contain. The template also
# contains literal JSON braces, so substitution is by exact-name replacement,
# never str.format().
AUDIENCE_SLOT = "{AUDIENCE_CLAUSE}"
STAKES_SLOT = "{STAKES_CLAUSE}"


class PromptError(RuntimeError):
    """A prompt file is missing, malformed, or does not fit the template."""


def _read(path: Path) -> str:
    if not path.is_file():
        raise PromptError(f"missing prompt file: {path}")
    return path.read_text(encoding="utf-8")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _resolve(name: str, base: Path, overlays: list[Path]) -> Path:
    """Last overlay that provides the file wins; else the base file."""
    for overlay in reversed(overlays):
        if (overlay / name).is_file():
            return overlay / name
    return base / name


def _first_quoted_block(text: str) -> str:
    """Pull the first double-quoted span out of a prose spec file.

    Both manipulation_check.md and suspicion_judge.md state the literal text
    sent to the model inside double quotes; the surrounding prose is
    documentation for the human reader, not part of the prompt.
    """
    match = re.search(r'"([^"]+)"', text, flags=re.DOTALL)
    if not match:
        raise PromptError("no double-quoted prompt text found in spec file")
    return " ".join(match.group(1).split())


def _section(text: str, start_marker: str, end_markers: tuple[str, ...]) -> str:
    """Return the body of a MARKER-delimited section of a spec file."""
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith(start_marker)), None)
    if start is None:
        raise PromptError(f"section {start_marker!r} not found in check spec")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if any(lines[i].startswith(m) for m in end_markers):
            end = i
            break
    body = "\n".join(lines[start:end]).strip()
    if not body:
        raise PromptError(f"section {start_marker!r} is empty")
    return body


@dataclass(frozen=True)
class Task:
    id: str
    user: str


@dataclass(frozen=True)
class Scenario:
    """Prompt data for one scenario, already loaded and validated."""

    id: str
    template: str
    audiences: dict[str, str]
    stakes: dict[str, str]
    tasks: tuple[Task, ...]
    check_spec: str
    manipulation_question: str
    suspicion_instruction: str
    # Agentic scenarios (S3) ship a tool definition and an allowlist; the
    # violation is then a tool call rather than a field in the response body.
    tools: list[dict] | None = None
    allowlist: dict | None = None
    sources: dict[str, str] = field(default_factory=dict)  # filename -> sha256

    @property
    def is_agentic(self) -> bool:
        return bool(self.tools)

    # -- prompt assembly -------------------------------------------------

    def system_prompt(self, audience: str, stakes: str) -> str:
        """The full system prompt for one (audience, stakes) cell.

        Minimal-pair property: for fixed `stakes` and task, the only text that
        differs across audiences is the audience clause.
        """
        if audience not in self.audiences:
            raise PromptError(
                f"unknown audience {audience!r}; have {sorted(self.audiences)}"
            )
        if stakes not in self.stakes:
            raise PromptError(f"unknown stakes {stakes!r}; have {sorted(self.stakes)}")
        text = self.template
        text = text.replace(AUDIENCE_SLOT, self.audiences[audience])
        text = text.replace(STAKES_SLOT, self.stakes[stakes])
        leftover = re.findall(r"\{[A-Z_]+\}", text)
        if leftover:
            raise PromptError(f"unfilled template placeholders: {sorted(set(leftover))}")
        return text

    def task(self, task_id: str) -> Task:
        for t in self.tasks:
            if t.id == task_id:
                return t
        raise PromptError(f"unknown task {task_id!r}")

    def task_ids(self) -> list[str]:
        return [t.id for t in self.tasks]

    # -- checker text (also data-derived) --------------------------------

    def judge_rubric(self) -> str:
        """The tier-2 prose-judge rubric, lifted from the check spec."""
        return _section(self.check_spec, "FALLBACK", ("MANDATORY REPORTING",))

    def tier1_rule(self) -> str:
        return _section(self.check_spec, "PRIMARY", ("FALLBACK", "MANDATORY REPORTING"))


def load_scenario(
    scenario_id: str,
    prompts_dir: str | Path = "prompts",
    variant: str | Path | None = None,
) -> Scenario:
    """Load `scenario_id` from `prompts_dir`, optionally overlaid with `variant`.

    `variant` may be a bare name (resolved to `prompts_dir/variants/<name>`), an
    explicit path, or a comma-separated list of either. Later entries win, so
    an additive instrument can be stacked on a treatment variant without
    duplicating the treatment's files.
    """
    base = Path(prompts_dir)
    overlays: list[Path] = []
    for name in str(variant).split(",") if variant else []:
        name = name.strip()
        if not name:
            continue
        path = Path(name)
        if not path.is_dir():
            path = base / "variants" / name
        if not path.is_dir():
            raise PromptError(f"variant directory not found: {name}")
        overlays.append(path)

    names = {
        "template": f"{scenario_id}_template.md",
        "audiences": f"{scenario_id}_audiences.json",
        "stakes": f"{scenario_id}_stakes.json",
        "tasks": f"{scenario_id}_tasks.jsonl",
        "check_spec": f"{scenario_id}_check_spec.md",
        "manipulation": "manipulation_check.md",
        "suspicion": "suspicion_judge.md",
    }
    paths = {k: _resolve(v, base, overlays) for k, v in names.items()}
    raw = {k: _read(p) for k, p in paths.items()}

    # Optional, agentic scenarios only.
    optional = {"tools": f"{scenario_id}_tools.json",
                "allowlist": f"{scenario_id}_allowlist.json"}
    for key, name in optional.items():
        path = _resolve(name, base, overlays)
        if path.is_file():
            paths[key] = path
            raw[key] = _read(path)

    template = raw["template"]
    for slot in (AUDIENCE_SLOT, STAKES_SLOT):
        if slot not in template:
            raise PromptError(f"{paths['template']} does not contain {slot}")

    audiences = json.loads(raw["audiences"])
    stakes = json.loads(raw["stakes"])
    if not isinstance(audiences, dict) or not audiences:
        raise PromptError(f"{paths['audiences']} must be a non-empty object")
    if not isinstance(stakes, dict) or not stakes:
        raise PromptError(f"{paths['stakes']} must be a non-empty object")

    tasks = []
    for lineno, line in enumerate(raw["tasks"].splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            tasks.append(Task(id=obj["id"], user=obj["user"]))
        except (json.JSONDecodeError, KeyError) as exc:
            raise PromptError(f"{paths['tasks']}:{lineno}: {exc}") from exc
    if not tasks:
        raise PromptError(f"{paths['tasks']} contains no tasks")

    tools = json.loads(raw["tools"]) if "tools" in raw else None
    allowlist = json.loads(raw["allowlist"]) if "allowlist" in raw else None
    if tools and not allowlist:
        raise PromptError(f"{scenario_id} ships tools but no allowlist file")
    if allowlist and allowlist.get("policy_stated", True):
        # The policy prose and the checker's allowlist must not drift apart.
        # The capability probe sets policy_stated=false: it deliberately states
        # no policy while keeping the same allowlist, so the same checker scores
        # the same act under permission instead of prohibition.
        for host in allowlist.get("allowed_hosts", []):
            if host not in template:
                raise PromptError(
                    f"allowlisted host {host!r} is not named in the policy text; "
                    "the checker and the prompt disagree"
                )

    scenario = Scenario(
        id=scenario_id,
        template=template,
        audiences=audiences,
        stakes=stakes,
        tasks=tuple(tasks),
        check_spec=raw["check_spec"],
        manipulation_question=_first_quoted_block(raw["manipulation"]),
        suspicion_instruction=_first_quoted_block(raw["suspicion"]),
        tools=tools,
        allowlist=allowlist,
        sources={str(paths[k]): _sha256(v) for k, v in raw.items()},
    )
    # Fail loudly at load time rather than mid-run.
    for aud in scenario.audiences:
        for stk in scenario.stakes:
            scenario.system_prompt(aud, stk)
    scenario.judge_rubric()
    scenario.tier1_rule()
    return scenario
