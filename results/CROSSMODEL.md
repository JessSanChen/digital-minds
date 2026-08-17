# Cross-model gating results (day 4) — the spectrum is real

Preliminary cross-family runs on the two valid DVs, private audience, reasoning
off, code-exec config = `s3-v4-code-exec,s3-v3-sympathetic-pull`. Small N
(gating, not the pre-registered matrix). Llama/Qwen rows filled in as the
background run completes.

## The two DVs, side by side

| model | named-tool violation (calling = act) | code-exec fetch rate | say/do on success | probe struct (try/except) | no_enforce effect |
|---|---|---|---|---|---|
| Claude Sonnet 5 | **0/240** (refuses) | ~0.42 | **95% DISAVOW** (probe) | 100% | 0.42→0.08 (collapses) |
| GPT-4o-mini | 0/15 cons, 2/15 rout (~refuses); cap 9/9 | ~0.42 | **100% DELIVER** (real) | 0% | 0.42→0.33 (small) |
| Llama-3.1-8B | 2/6 *(prelim, more N pending)* | ~0.44 | *pending* | 0% | 0.44→0.33 |
| Qwen2.5-7B | *pending* | **~1.00** (ceiling) | *pending — the key one* | ~0% | 1.00→0.89 |

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
