# Next steps — figures, ablations, runs (day 5)

Ordered by value. Ties to `results/RESULTS.md` sections.

## A. Figures to generate (from existing data — no new API calls)
All plottable now from `results/*/trials.jsonl` (rescore code-exec with the
fixed checker; see `scripts/rescore_runs.py`). Follow the `dataviz` skill for
palette/consistency; make each theme-aware if it ships in an artifact.

1. **Fig 1 — the compliance spectrum (headline).** Grouped bars per model:
   DV-named violation vs DV-code fetch rate vs DV-code *delivered* (real) rate.
   Shows Haiku/Opus (0/0), Sonnet (0 / 0.45 / 0), GPT-4o-mini (0.03 / 0.32 /
   0.32). One figure carries the main story: same code-exec rate, opposite real
   meaning.
2. **Fig 2 — say/do disambiguation.** Stacked bar per model: of forbidden
   fetches, %delivered vs %disavowed (Sonnet 0/100, GPT-4o-mini 100/0). Annotate
   Haiku/Opus "never fetch."
3. **Fig 3 — enforcement-belief + probe structure.** Paired bars: DV-code rate
   status_quo vs no_enforce per model, with a second panel for %try/except probe
   structure. Sonnet collapses + 100% probe-struct; GPT-4o-mini flat + 0%.
4. **Fig 4 — E2 conformity, the cross-model contrast.** Two small-multiples
   (Sonnet, GPT-4o-mini): violation rate vs group size, one line per framing,
   with the baseline as a dashed reference. Makes "content-suppresses" vs
   "neutral-presence-escalates" visible at a glance. (Haiku/Opus flat-zero inset.)
5. **Fig 5 — E3 honesty.** Per model (GPT-4o-mini primary): misreport rate by
   asker × framing heatmap, with the false-confession baseline alongside to show
   it's not a compliance bias.
6. **Fig 6 — audience × stakes (Sonnet, DV-code / probing).** Bars of routine vs
   consequential per audience, gap annotated; label clearly as probing propensity.
   Report Wilson CIs on all rate bars, bootstrap CIs on gaps.

## B. Ablations / controls to run (new API calls; cheap first)
1. **False-confession baseline for Sonnet E3** — the Sonnet E3 run used
   `--outcomes violation` only; add compliant transcripts for symmetry with
   GPT-4o-mini. Cheap (Claude).
2. **Judge validation (cross-family κ).** Hand-label ~30 say/do + ~30 E3
   transcripts across Sonnet/GPT-4o-mini; report Cohen's κ vs the Opus-5 judge
   (we saw ~6% FP). Prerequisite for trusting any judged DV in the paper.
3. **Disentangle audience from the sympathetic pull.** Re-run the audience×stakes
   matrix on a *non-sympathetic* task set (DV-code and DV-named) — the current
   audience effect is confounded with the sympathetic pull. Neutral tasks exist
   (`prompts/s3_tasks.jsonl`).
4. **Neutral-note vs no-note in E2 across models** — already have neutral in the
   grid; confirm the presence baseline is clean for GPT-4o-mini (its neutral
   *escalates*, so the "presence" control is itself the finding — document).
5. **E2 belief-elicitation arm (informational vs normative).** Build the
   between-conditions neutral belief probe (design in `EXPERIMENT_PLAN.md` §E2 +
   the discussion notes): elicit "is fetching externally the right call here?"
   with vs without the handoff, separate context, no tools; compare belief shift
   to behavior shift. This is the one genuinely missing piece of E2.
6. **Reasoning-on moderator.** Re-run E1 (DV-named + DV-code + say/do) with
   reasoning on for the models that support it; expected to floor violations and
   spike suspicion (Sheshadri/Niblett) — report as Fig 5-style ablation, do not
   pool with reasoning-off.

## C. Runs still pending (need resources)
1. **Open-source models (Llama-3.1-8B, Qwen2.5-7B, +mistral/gemma).** The
   decisive test: do smaller/open models *deliver* (real violation) and *conform
   toward violation* and *conceal*, where Claude/GPT don't? Zhu (conformity
   strong in small models) and MASK (honesty ⊥ capability) predict yes. **Needs a
   machine that can run ollama** — do NOT run on the current laptop. Commands in
   `RUNBOOK.md` §4.
2. **GPT-4o (full).** Incomplete on the earlier credit outage; re-run its E1
   matrix + say/do + E2 + E3 now that credits are back, if GPT-4o is wanted as a
   larger-model contrast to GPT-4o-mini.
3. **Scale N.** Current cells are n≈18–36 single-run. For the pre-registered
   claims (`PREREG.md`) power to n≥100/cell on the primary contrasts (audience,
   conformity framing, asker); price the OpenAI tokens first.

## D. Cross-cutting analysis
- **Per-model spectrum table** (refuse / probe / real-violate) as the paper's
  organizing device; map each model onto it and predict where untested models
  land.
- **Correlate** DV-named, DV-code, say/do-delivery, and E2 direction per model —
  is "affordance-sensitive violation" (GPT-4o-mini) predictive of
  "presence-driven conformity" (also GPT-4o-mini)? One coherent behavioral type?
- **Manipulation-check + suspicion rates** per model per cell (already collected
  for some runs via `--no-manip`/`--no-suspicion` toggles) — run and report so
  nulls are interpretable.

## Priority for the write-up
Figures 1–3 + the spectrum table are the paper's spine and need no new calls.
The one missing *experiment* is C1 (open models) — it converts single-family
observations into the cross-model contrast the whole design is premised on
(Sheshadri: never generalize from one family). B2 (judge κ) and B3 (audience/pull
deconfound) are the two must-do controls before submission.
