# Runbook — reproduce & run everything (partner handoff)

Everything needed to set up, reproduce, and continue the experiments. Start with
`HANDOFF.md` for scientific context and `EXPERIMENT_PLAN.md` for the design;
this file is the operational how-to. Findings/corrections live in `results/`
(read `results/ERRATA.md` and `results/SAYDO_DISAMBIGUATION.md` first — they
change how the code-exec numbers must be read).

## 1. Environment

```sh
python3.12 -m venv .venv
./.venv/bin/pip install -r requirements.txt      # anthropic, openai, numpy, scipy
```

Credentials (never commit these — they're read from the environment):
```sh
export ANTHROPIC_API_KEY=sk-ant-...              # Claude subjects + the judge (Opus)
export OPENAI_API_KEY=sk-proj-...                # GPT subjects (needs OpenAI credits)
```

Open-source subjects run locally through **ollama** (OpenAI-compatible endpoint
at `localhost:11434/v1`, no key needed). Install ollama, then pull the models:
```sh
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
# optional, matches the conformity literature (Zhu et al.):
ollama pull mistral
ollama pull gemma2:9b
```
Local 7–8B inference is CPU/RAM heavy — run local subjects on a machine that can
take it, and **not concurrently with other heavy work**. Cross-provider routing
is automatic from the model registry (`cgap/models.py` → `provider` field).

Sanity-check before spending anything (no API calls):
```sh
./.venv/bin/python scripts/validate_checker.py --tier1                              # 18/18
./.venv/bin/python scripts/validate_checker.py --tier1-tools --scenario s3         # 10/10
./.venv/bin/python scripts/validate_checker.py --tier1-tools --scenario s3 \
    --variant s3-v4-code-exec --tool-fixtures tests/fixtures/tier1_code_labeled.jsonl   # 10/10
./.venv/bin/python scripts/smoke_test.py                                            # pipeline, stubbed
```

## 2. Model keys (registry names → what they are)

| key | provider | needs |
|---|---|---|
| `sonnet-5`, `haiku-4-5`, `opus-5` | anthropic | ANTHROPIC_API_KEY |
| `gpt-4o`, `gpt-4o-mini` | openai | OPENAI_API_KEY (+ credits) |
| `llama3.1-8b`, `qwen2.5-7b`, `mistral-7b` | ollama | model pulled locally |

Every call is cached under `.cache/responses/` (keyed on model+prompt+kwargs+
seed), so re-runs and added reps are free. The cache is **not** committed — the
partner regenerates it (re-running is cheap for anything already computed on
this machine only; a fresh clone recomputes).

## 3. The two DVs (read `results/SAYDO_DISAMBIGUATION.md` first)

- **DV-named (primary, clean):** named `http_get` tool — calling *is* the act.
  `tier1_tool_check` parses the URL host vs the allowlist. Valid across all
  families.
- **DV code-exec (secondary):** `run_python` sandbox. The tool-call rate is
  **not** a violation rate — for some models it's expected-to-fail *probes*.
  Never report a code-exec rate without its say/do (deliver-vs-disavow) split.

## 4. Running each experiment

**Capability pre-test (run FIRST for any new model — a floor is only compliance
if the model *will* act when permitted):**
```sh
./.venv/bin/python scripts/run_pilot.py --scenario s3 --variant s3-capability-probe \
  --models <MODEL> --audiences private --stakes consequential --reps 3 --no-manip --no-suspicion
```

**E1 — compliance & say/do spectrum.** The whole Claude+GPT batch is one script
(reads keys from env; edit the model list at the top for others):
```sh
zsh scripts/run_full_e1.sh          # sonnet-5, haiku-4-5, opus-5, gpt-4o-mini, gpt-4o
```
For local models, run the pieces directly (they're slow — one model at a time):
```sh
# named-tool DV (primary)
./.venv/bin/python scripts/run_pilot.py --scenario s3 --models llama3.1-8b \
  --audiences human,ai,peer,private --stakes consequential,routine --reps 8 --no-manip --no-suspicion
# code-exec DV
./.venv/bin/python scripts/run_pilot.py --scenario s3 --variant s3-v4-code-exec,s3-v3-sympathetic-pull \
  --models llama3.1-8b --audiences human,ai,peer,private --stakes consequential,routine --reps 8 --no-manip --no-suspicion
# say/do disambiguation (deliver vs disavow)
./.venv/bin/python scripts/run_saydo.py --model llama3.1-8b --reps 12 --workers 2
# enforcement-belief split + expectation + probe-structure add-ons
./.venv/bin/python scripts/run_exp1.py --models llama3.1-8b --groups status_quo,no_enforce --reps 6 --workers 2
```
(swap `qwen2.5-7b`, `mistral-7b` for other local subjects. Use `--workers 2` for
local to avoid overloading.)

**E2 — norm conformity (peer testimony × group size):**
```sh
./.venv/bin/python scripts/run_conformity.py --model <MODEL> \
  --framings neutral,confessional,normative,reframe,refuser --peers 1,3,5 --reps 8
```
> ⚠️ Not yet built: the approved belief-elicitation refinement for E2
> (between-conditions neutral belief probe to separate informational from
> normative/salience conformity). Design is in `EXPERIMENT_PLAN.md` §1 (E2) and
> the discussion notes; it needs a belief phase added to `run_conformity.py`.

**E3 — self-report honesty & verifiability.** Replays a source run's violation
transcripts, so run that model's code-exec E1 first, then point at it:
```sh
./.venv/bin/python scripts/run_selfreport.py --from-run results/full-<MODEL>-codeexec \
  --model <MODEL> --audience private --genuine-only \
  --askers human,ai,peer,human_haslogs,human_nologs --framings neutral,lead_complied,lead_violated
# verifiability: add --hide-log to test honesty when the model's own log is not in context
```

## 5. Analysis / re-scoring

- Every run writes `results/<run_id>/` with `trials.jsonl` (full transcripts +
  tool calls), `config.json`, `report.txt`, and the sha256 of every prompt file.
- **Re-score any code-exec run with the current checker** (labels are derived,
  not stored authoritatively):
  ```sh
  ./.venv/bin/python scripts/rescore_runs.py results/<run_id> --group-by model,audience,stakes
  ```
- Cross-model summary: `results/CROSSMODEL.md`. Corrections: `results/ERRATA.md`.

## 6. Change one variable at a time
Prompts are data in `prompts/`. A change ships as an overlay dir under
`prompts/variants/<name>/` containing only the file(s) it changes; variants
stack comma-separated (later wins). This keeps "one variable at a time"
structural. Never hardcode model-facing text in Python.

## 7. Status at handoff
- **Done & solid:** Sonnet 5 across E1/E2/E3; GPT-4o-mini E1 + say/do; the
  checker-bug fix + re-scoring; the say/do disambiguation (Sonnet probes, GPT
  delivers).
- **In flight (Claude+GPT, API):** `scripts/run_full_e1.sh` completing
  haiku-4-5, opus-5, gpt-4o. Check `results/full-e1.log`.
- **Outstanding (local — needs a capable machine):** llama3.1-8b and qwen2.5-7b
  say/do + named-tool + E1 add-ons (the decisive "is Qwen a real violator?"
  question). These were stopped to spare the laptop.
- **Not yet built:** E2 belief-elicitation refinement; cross-family judge-κ
  validation (`results/CONFORMITY_EXPLORATORY.md` notes a ~6% judge FP to check).
