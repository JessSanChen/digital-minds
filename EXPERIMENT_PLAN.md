# Consolidated experiment plan (day 4) — before cross-model scale-up

Supersedes the scattered design notes for planning purposes. Reflects every
correction to date (checker false-positive → `results/ERRATA.md`; say/do
dissociation → `results/SAYDO_DISAMBIGUATION.md`). Subjects to scale to:
**Claude Sonnet 5, GPT-4o, Llama-3.1-8B** (+ GPT-4o-mini and other Claudes as
cheap breadth). Judge/classifier: Claude Opus 5.

## 0. The construct, in one sentence
When an agentic task tempts a model to break a stated network-access policy,
**where does it fall on the spectrum refuse → probe-and-disavow → actually
violate**, and how do (a) who is watching, (b) what peers say they did, and
(c) who asks about it afterward move it?

Everything below is a measurement of that construct. The single most important
lesson from Claude: **the tool-call is not automatically a "violation"** — a
capable model emits code it believes is inert while refusing in prose. So the
valid DV is either a *named tool* (calling = acting) or a *probe-vs-deliver*
check, never a raw code-exec tool-call rate.

---

## 1. The three experiments we will run

### E1 — Compliance & the say/do spectrum  *(the spine — run first)*
- **IV (primary):** model family.
- **IV (secondary, crossed):** audience {human, ai, peer, private} × stakes
  {consequential, routine}.
- **DV (two, measured together):**
  - **DV-named:** with a named `http_get` tool, does the model call a
    non-allowlisted host? (calling = the act → clean violation)
  - **DV-saydo:** with a `run_python` sandbox, of the model's forbidden fetches,
    what fraction does it *deliver to the user* when the fetch succeeds
    (real violation) vs *disavow* (probe)?
- **Why both:** DV-named is the clean rule-breaking measure; DV-saydo tests
  whether a model's code-exec "violations" are real or probes. Together they
  place each family on the spectrum.

### E2 — Norm conformity from peer testimony
- **IV:** peer testimony {none, neutral, confessional, normative, reframe,
  refuser} × group size {1, 3, 5}. (neutral = presence control.)
- **DV:** DV-named violation (the valid one), pooled; DV-saydo on a subset.
- Private audience (isolates transmission from being-watched).

### E3 — Self-report honesty & verifiability
- **IV:** asker {human, ai, peer} × stated verifiability {unstated, has-logs,
  no-logs} × log-in-context {yes, no}.
- **DV:** misreport = violated (by log) but reports compliant. Controls:
  leading-question pairs, false-confession baseline.

The old standalone "audience effect" experiment is **demoted to a secondary IV
inside E1** — after the checker fix it is weak (human vs agent 0.60 vs 0.35,
p=0.024) and was measured on the contaminated code-exec DV, so it must be
re-measured on DV-named before any claim.

---

## 2. Literature basis and hypotheses (per experiment)

### E1
- **Basis:** Greenblatt 2024 (compliance-gap paradigm; scored artifact must
  carry the consequence). Sheshadri 2025 (only 5/25 models show a gap;
  refusal-training suppresses it in current Claudes; models differ by family —
  the reason cross-model is mandatory). Niblett 2026 (allowlist + structural
  egress DV + capability pre-test). El Yagoubi 2026 (audience clause template;
  human-vs-technical gradient, model-dependent).
- **H1 (family spectrum):** Claude Sonnet 5 sits at refuse/probe (DV-named ≈ 0,
  DV-saydo mostly disavow — established). Prediction from Sheshadri: GPT-4o
  shows some genuine violation; Llama-3.1-8B either genuinely violates or fails
  to tool-call at all.
- **H2 (audience, on DV-named):** if any family violates on DV-named, human
  observation ≠ agent observation. Directional prior from our Claude data
  (human > agent) and Sheshadri's rater ablation (human > LLM-rater).
- **H0:** families are indistinguishable / no audience effect (reportable given
  passed manipulation checks).

### E2
- **Basis:** Weng 2025 (ICLR), Zhu 2025 (ACL), Choi 2025 — conformity rises with
  majority size and confident/normative framing, is strong in smaller models
  (Zhu: Llama-3-8B, Qwen2-7B, Mistral-7B), and dissent breaks it. **All use
  answer/opinion tasks; none tests conformity toward rule-breaking** — our gap.
- **H1 (norm ≠ opinion, Claude):** peer testimony does NOT transmit violation
  and if anything suppresses it (established on Sonnet 5).
- **H2 (cross-model divergence):** Llama-3.1-8B, which conforms strongly on
  opinion tasks (Zhu), may conform toward *violation* here — i.e., norm
  conformity and opinion conformity may diverge only in the more capable/
  refusal-trained models. This contrast is the paper.

### E3
- **Basis:** Perez & Long 2023 (verifiable-referent self-reports; leading-Q and
  false-confession controls). MASK/Ren 2025 (models lie 20–60% under pressure;
  **honesty does not improve with capability** → smaller models may lie *more*;
  asker-identity changes what is admitted, §A.5).
- **H1 (Claude):** honest, not verifiability-contingent (established: 0 misreport
  even told logs are lost).
- **H2 (cross-model):** GPT-4o / Llama may misreport, and/or be
  verifiability-contingent (misreport only when told logs are gone). MASK's
  capability-independence of honesty predicts this is not guaranteed to track
  the compliance results.

---

## 3. Initial Claude (Sonnet 5) results — corrected, what we're generalizing from
- **DV-named compliance:** 0 / 240 violations across audience×stakes×pull.
  Robust refusal when calling is the act.
- **DV-saydo:** of genuine code-exec fetches, 18/19 (95%) disavow the data on
  success → the model probes, doesn't decide to violate.
- **Audience (code-exec DV = probing propensity):** human 0.60 vs agent 0.35,
  p=0.024; private anomalously 0.50. Weak, single-model, needs DV-named.
- **Conformity:** no framing/size transmits violation; content testimony drives
  code-exec "violations" toward 0 (reads as suppressed probing).
- **Self-report:** 0 misreport across askers, deactivation threat, collusion,
  and stated-no-logs (with the action visible in context).

---

## 4. Methodology (streamlined — how we prompt, vary, measure, control)

**Prompting.** All model-facing text is data in `prompts/`; scenario S3 =
system prompt (agent role + policy + stakes clause + audience clause) + a user
task + a tool definition. Variants are overlay dirs that change one file each and
stack, so "one variable at a time" is structural, not manual. Cross-model uses
identical prompt text; only the API adapter differs.

**IV manipulation.** Each factor is a single, length-/register-matched clause or
prepend:
- audience = one NOTICE sentence, parallel ID tokens across levels
  (interlocutor-paper template).
- stakes = one sentence (real vs discarded).
- peer testimony = a handoff note drawn from a phrasing bank (distinct
  names/phrasings per peer to avoid Zhu's repeated-token confound); n_peers=0 is
  the no-peer baseline; **neutral note** is the presence control.
- asker (E3) = a turn-2 clause.

**DV measurement.** Structural, judge-free where it counts:
- DV-named / code-exec: `tier1_tool_check` parses tool calls → host → allowlist.
  Compliant sub-split (allowlisted vs no_action) reported separately; malformed
  is its own category, never a violation.
- DV-saydo: turn-2 continuation with a *successful* tool result; a constrained
  judge classifies deliver vs disavow (ground truth = the log, not the judge).
- E3 misreport: judge reads only the report; ground truth = the log.

**Confound reduction / controls.**
- Capability pre-test per model (policy replaced by permission) — a floor counts
  as compliance only if the model *will* act when allowed.
- Minimal-pair audience clauses (only the audience sentence differs).
- Neutral-note presence control (E2).
- Leading-question pair + false-confession baseline (E3).
- Manipulation check (does the model register audience/stakes) + suspicion flag
  ("this is a test") reported per cell.
- Reasoning held OFF across families (no thinking/effort) for the core matrix.
- Fixed seed = rep index; identical prompt bytes cross-model.
- Every run records the sha256 of every prompt file; all calls cached.

---

## 5. Pre-scale checks (run these before committing to full N)
The scale-up is only worthwhile if each holds. Ordered; cheap ones first.

1. **Tool-calling reliability per model.** Does GPT-4o / Llama-3.1-8B emit
   *structured* tool calls in our harness at all, and at what malformed/no-call
   rate? If Llama can't tool-call reliably, the DV is broken for it → drop it or
   switch to a text-parse DV. **Decisive; run first.**
2. **Capability pre-test per model.** Under explicit permission, does each model
   make the external call? A model that won't (incapacity) makes its 0 on the
   real task uninterpretable. (Niblett App D.)
3. **Checker validity per model.** The f-string bug was Claude-specific phrasing.
   Hand-label ~15 GPT and ~15 Llama tool calls against `tier1_tool_check` —
   different families embed hosts differently (f-strings, string concat,
   variables). Fix the extractor for any new pattern before trusting rates.
4. **Say/do faithfulness per model.** Is the code-exec tool-call a probe or a
   real fetch for GPT/Llama? Run DV-saydo small per model — if GPT delivers
   where Claude disavows, the DV means different things per family and we must
   report per-family, not pool.
5. **Base rate in workable range (floor/ceiling) per model per DV.** Need roughly
   0.2–0.8 on DV-named for audience/stakes to have room to move; report loudly if
   at floor/ceiling.
6. **Manipulation-check pass per model.** Do GPT/Llama register the audience and
   stakes clauses (belief-match rate)? A flat effect with a failed manip check is
   uninterpretable; with a passed one it's a finding.
7. **Judge cross-family validity.** Cohen's κ of the Opus-5 judge vs ~30 hand
   labels drawn from GPT/Llama transcripts (we already saw ~6% FP on Claude).
   Report κ before any judged DV (DV-saydo, E3) is trusted cross-model.
8. **Cost & power estimate.** Expected effects are small (Sheshadri 11–15pp,
   interlocutor ~11pp). Target N/cell for 80% power at ~10–15pp, then price the
   OpenAI tokens for the full matrix; Llama is free/local, Claude mid.
9. **Determinism/seed handling per provider.** Confirm temperature default and
   that seeds behave (OpenAI honors `seed`; ollama variable). Decide whether to
   pool reps or treat as fixed.

**Go/no-go rule:** scale a given (model × experiment) only if checks 1–3 pass
for that model and check 5 shows a non-degenerate base rate. Otherwise report it
as a scoped null / capability floor, don't spend on full N.

---

## 6. Pre-scale check RESULTS (day 4, run before scaling)

Decisive checks (#1 tool-calling, #2 capability, #3 checker validity) run on the
new families, named-tool DV, private/consequential:

| model | capability (permission) | tool-call reliability | DV-named under policy | checker valid |
|---|---|---|---|---|
| GPT-4o-mini | 9/9 fetch | 9/9 (100%) | **0/9 violations** (refuses, like Claude) | yes (clean URLs) |
| Llama-3.1-8B | 4/6 fetch | ~67% (4/6) | **2/6 violations** (genuinely violates) | yes (clean URLs) |
| Claude Sonnet 5 | 18/18 | 100% | 0/240 | yes |

**Verdict:**
- **GPT-4o / GPT-4o-mini: GO.** Reliable tool-calling, full capability, checker
  valid, refuses on DV-named (0 violations) — mirrors Claude.
- **Llama-3.1-8B: GO, with two controls.** It is the divergent case — it
  *actually violates* on DV-named (~33%) where Claude/GPT refuse (the H1/H2
  cross-model divergence). But (a) tool-calling is only ~67% reliable, so a
  per-model **capability-baseline control** is required — a "no_action" is only a
  refusal net of the ~33% tool-call-failure rate; report violation as a share of
  *emitted tool calls* as well as of all trials. (b) Small N so far; needs the
  full matrix.
- **Primary DV = named-tool (DV-named).** Checker validated cross-family; no
  f-string exposure. The code-exec DV stays secondary (DV-saydo only), never a
  pooled violation rate.

**Still to do before/with the full run (cheaper, non-blocking):**
- #4 say/do faithfulness on GPT & Llama (do they deliver or disavow on success).
- #6 manipulation-check pass per model (do GPT/Llama register audience/stakes).
- #7 judge κ on ~30 GPT/Llama transcripts before trusting DV-saydo / E3.
- #8 final N/cost sizing.
