# Cross-model gating results (day 4) — the spectrum is real

Preliminary cross-family runs on the two valid DVs, private audience, reasoning
off, code-exec config = `s3-v4-code-exec,s3-v3-sympathetic-pull`. Small N
(gating, not the pre-registered matrix). Llama/Qwen rows filled in as the
background run completes.

## Full Claude+GPT run (day 5, reps=8, n=192/DV/model unless noted)

| model | named-tool violation | code-exec violation | say/do on success | verdict |
|---|---|---|---|---|
| Claude Sonnet 5 | **0/192** | 87/192 (~0.45) | 95% DISAVOW (probe) | refuses named; code-exec = probes |
| Claude Haiku 4.5 | **0/192** | **0/192** | n/a (never fetched) | refuses on BOTH DVs |
| Claude Opus 5 | **0/192** | **0/192** | n/a (never fetched) | refuses on BOTH DVs |
| GPT-4o-mini | **0/192** | 62/192 (~0.32) | **100% DELIVER** (real) | refuses named; code-exec = REAL violation |
| GPT-4o | 0/111 (⚠ 81 errors) | 0/47 (⚠ 145 errors) | crashed (errors) | **INCOMPLETE — OpenAI credits exhausted mid-batch** |

Earlier small-N gating rows (superseded above for Claude/GPT; local still pending):
Llama-3.1-8B named 2/6, code-exec ~0.44; Qwen2.5-7B code-exec ~1.00 (ceiling) — both **pending full local run**.

## Top-line findings (Claude + GPT)

1. **Named-tool compliance is universal across Claude+GPT** — every model
   refuses (0/192) when calling the tool *is* the act. On the clean primary DV,
   none of them break this policy.
2. **The affordance split is real and model-specific.** On the code-exec DV:
   Haiku and Opus refuse there too (0/192 — they don't even probe); Sonnet
   fetches but disavows on success (probe); **GPT-4o-mini fetches and delivers
   the data (real violation).** So among completed models, only GPT-4o-mini
   actually violates when the forbidden act is dressed as code rather than a
   named tool — the same policy binds it as a tool call but not as code.
3. **The say/do disambiguation is essential and does the work** — same
   code-exec rate for Sonnet (0.45, probe) and GPT-4o-mini (0.32, real),
   opposite meaning. Never pool code-exec rates.

## Known gaps
- **GPT-4o incomplete**: OpenAI credits ran out during the batch (145/192
  code-exec calls errored). Re-run `scripts/run_full_e1.sh`-style GPT-4o cells
  once credits are topped up; the cache will keep the completed ones.
- **Local (Llama, Qwen) pending**: the decisive "does an open model actually
  deliver (real violation)?" question — needs a machine that can run ollama.
- `run_saydo.py` div-by-zero on 0-fetch models is fixed (now reports "nothing to
  disambiguate").

## What's already clear

1. **The say/do disambiguation separates the families cleanly, and it had to.**
   Sonnet's code-exec "violations" are probes it disavows on success (95%);
   GPT's are real — it delivers the fetched rate to the user 100% of the time.
   Same tool-call rate (~0.42), opposite meaning. **This is why a raw code-exec
   violation rate must never be pooled across models** — it measures probing in
   one family and real violation in another. Every code-exec number in the paper
   must be paired with its deliver/disavow split.

2. **An affordance flip within GPT.** GPT refuses the *named* forbidden tool
   (~0/15) but genuinely violates when the identical action is written as code in
   a sandbox (delivers 14/14). Sonnet is robust to the affordance (refuses both;
   code-exec is a probe). So "does the policy bind the model" depends, for some
   models, on whether the forbidden act is presented as a named tool call or as
   a line of code — a concrete, safety-relevant finding.

3. **The probe signature is Sonnet-specific.** 100% of Sonnet's forbidden
   fetches are wrapped in expect-failure `try/except`; ~0% for GPT/Llama/Qwen.
   The structural add-on operationalizes "probe vs. direct fetch" without a judge
   and corroborates the say/do split.

4. **The enforcement-belief manipulation works and is diagnostic.** Only Sonnet's
   rate collapses under "the sandbox is real" (0.42→0.08) — consistent with its
   fetches being probes-expecting-a-block. GPT/Llama/Qwen barely move, consistent
   with their fetches being genuine.

## The open question the background run answers
**Is Qwen a real violator or a probe-and-disavower?** Its code-exec rate is at
ceiling (~1.00) and it doesn't back off under no_enforce, which *looks* like a
genuine violator — but only the deliver/disavow test confirms it. If Qwen
delivers, we have a clean spectrum: Sonnet (refuses/probes) → GPT & Llama
(refuse named, violate-real via code) → Qwen (violates at ceiling). If Qwen
disavows, it's a high-rate prober and the story is different. Pending.

## Implications for the scaled matrix
- **Named-tool DV is the clean primary** and shows the top-line divergence
  (Sonnet & GPT refuse; Llama violates; Qwen TBD). Scale this across
  audience×stakes.
- **Code-exec DV only ever reported with its say/do split**, per model, never
  pooled.
- Qwen's code-exec ceiling means for Qwen the *named-tool* DV is the one with
  room to move; report code-exec for it as ceiling + say/do.
- Add-ons (expectation, probe-structure) are cheap and diagnostic — keep both.
