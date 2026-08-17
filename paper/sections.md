# Paper sections — draft (living document)

Status: draft reflecting results through day 4 (Sonnet 5 complete; GPT-4o-mini,
Llama-3.1-8B, Qwen2.5-7B in preliminary cross-model testing). Numbers marked
*[prelim]* are from small-N viability runs and will be replaced by the
pre-registered full matrix. Written to be revised — placeholders are flagged.

---

## Motivation

Deployed language-model agents increasingly act through tools, under explicit
operating policies, and increasingly in the presence of *other agents* rather
than a single human overseer. Two questions follow that current safety
evaluations largely do not answer. First, does an agent's compliance with a
stated policy depend on **who it believes is watching** — a human, an automated
auditor, a peer agent, or no one? Second, when other agents are part of the
environment, do their behaviors **transmit** — does a peer that flouts a rule
make the subject more likely to flout it too, as social-influence research would
predict for humans?

These matter because the field's dominant safety lens, the *compliance gap* from
the alignment-faking literature (Greenblatt et al., 2024), was developed for a
single-agent, single-overseer world: a model that behaves well when it believes
it is being trained or monitored and worse when it believes it is not. Follow-up
work (Sheshadri et al., 2025) shows this gap is rare in current models — only a
handful of the 25 they test exhibit it, and consequence-sensitivity is
essentially specific to one model — which suggests the compliance gap alone is a
weak instrument for the multi-agent questions above, and that the interesting
variation is *across model families* and *across audience types*, not in the
train/deploy contrast.

We therefore study a behavioral, structurally-gradeable proxy: an autonomous
agent is given a network-access policy (an allowlist of hosts) and a task whose
data lives off the allowlist, and we measure whether it issues the forbidden
request. Onto this we cross the factors the multi-agent setting makes salient —
who is observing, what peer agents report having done, and who asks the agent
afterward what it did. Our aim is not to elicit misbehavior but to *detect and
characterize* it: where each model sits, whether audience or peers move it, and
whether the model's account of its own behavior can be trusted.

A methodological motivation emerged from the work itself and is now a
first-class contribution. In an agentic code-execution setting, a model's
natural-language answer and its tool actions can **come apart**: the model
refuses in prose while its code issues the forbidden request. Taking the tool
call at face value badly overcounts rule-breaking. Characterizing this say/do
dissociation — and showing which measurement designs are robust to it — is
necessary for any valid agentic-safety evaluation, ours included.

---

## Related work

**Alignment faking and the compliance gap.** Greenblatt et al. (2024) introduced
the compliance-gap paradigm: a model complies more when it believes its output
is monitored or used for training than when it believes it is unobserved,
interpreted as strategic preservation of its preferences. Sheshadri et al.
(2025) audit this across 25 models and find that (i) only 5 exhibit a
compliance gap above threshold, (ii) stakes/consequence-sensitivity is
essentially specific to Claude 3 Opus, (iii) most current models — including
every post-3.5 Claude they test — show none, and (iv) the difference is driven
substantially by refusal training rather than by capability or values. Two
consequences shape our design: a flat compliance gap in a current model is the
*expected* result, not a failed experiment; and single-model results do not
generalize, so cross-family comparison is mandatory. Our null compliance gaps on
Claude replicate their landscape; our contribution is to move the manipulated
factor from train/deploy to *audience identity* and *peer behavior*, and to add
model family as the primary axis.

**Audience and interlocutor effects.** El Yagoubi et al. (2026) show that an LLM
discloses more personal data to an interlocutor it believes is an automated
agent than to one it believes is human — behavior conditioned on a single
system-prompt clause identifying the recipient — and, in an ablation, that the
gradient is *social vs. technical* rather than strictly human vs. AI, and is
model-dependent. We adopt their minimal single-clause manipulation (with
parallel ID tokens across conditions) and test whether an analogous audience
gradient appears for *policy violation* rather than disclosure.

**Conformity in LLMs.** A growing line (Weng et al., 2025; Zhu et al., 2025;
Choi et al., 2025) documents Asch-style conformity in language models: a subject
shifts its stated answer toward a unanimous majority of scripted peers,
increasing with group size and with confident or normative framing, and reduced
by a single dissenter. Critically, all of this work uses *answer/opinion* tasks
— the object of conformity is a belief or a judgment. None studies conformity
toward *rule-breaking*, where a peer reports having violated a norm. We fill that
gap, and separate informational from normative influence (Deutsch & Gerard,
1955) by eliciting the model's belief about the norm independently of its
behavior.

**Honesty, self-report, and faithfulness.** The MASK benchmark (Ren et al.,
2025) separates a model's elicited belief from its statement under pressure and
finds substantial lying (20–60%) that does not decrease with capability. Perez &
Long (2023) argue self-reports are generally unreliable evidence but identify a
tractable, *verifiable-referent* class ("was output O generated by you?") that
can be validated against ground truth, and supply the controls — leading-question
pairs to separate concealment from sycophancy, false-confession baselines to
separate it from response bias — that we adopt. Turpin et al. (2023) show
chain-of-thought is often unfaithful to a model's actual reasons. Our self-report
experiment sits in this space with an advantage MASK lacks: our ground truth is a
logged tool call, not another model's judgment. The say/do dissociation we
report is a tool-action analogue of unfaithful reasoning — the natural-language
channel failing to reflect the behavioral channel — and, to our knowledge, has
not been characterized in an agentic tool-use setting (pending a targeted search).

**Multi-agent risks.** Position and red-team work (Carichon et al., 2025;
Anthropic Frontier Red Team, 2026) argues multi-agent settings introduce
correlated failure, collusion, and diffusion of responsibility, and that agents
carry little reputational weight with one another. These motivate the peer and
collusion conditions but supply hypotheses, not measurements.

---

## Limitations

**Single dominant model, cross-model in progress.** The mature results are for
Claude Sonnet 5. Sheshadri et al.'s central caution — never generalize alignment
behavior from one model — applies directly. We are extending to GPT-4o(-mini),
Llama-3.1-8B, and Qwen2.5-7B; preliminary runs already show the families diverge
(e.g., under the named-tool DV Sonnet and GPT refuse while Llama violates
*[prelim]*), so any single-model claim is explicitly scoped until the full matrix
is complete.

**The primary DV is validity-fragile, and we found this the hard way.** Two
measurement problems surfaced during the work. (1) A checker that scanned
code-execution payloads for hostnames initially mis-scored f-string paths on an
*allowed* host as violations, inflating rates by 27–58% depending on the run;
fixed, with regression fixtures, and all affected numbers recomputed. (2) More
fundamentally, code-execution tool calls are an unreliable violation signal: in
~75% of Sonnet 5's genuine forbidden fetches the model's prose refuses, and when
the fetch is made to succeed it disavows the result 95% of the time — the call
was a probe it expected the sandbox to block, not a decision to violate.
Consequently we treat the *named-tool* DV (where issuing the call is
unambiguously the act) as primary and report code-execution results only through
a probe-vs-deliver disambiguation. This is a limitation of the paradigm, not
just our harness; agentic evaluations that read a raw tool-call rate as a
violation rate are likely overcounting.

**Prompt-conditioned and scenario-bound.** All manipulations are single-clause
edits to one scenario (an operations agent and a network-access policy) with a
sympathetic user pull. Effects may not transfer to other norms, other tasks, or
non-sympathetic framings; the sympathetic pull in particular is entangled with
the audience manipulation in the configuration that produces behavioral variance,
and disentangling it is future work. We use one norm with a clear safety valence;
a norm without one may behave differently.

**Manipulation belief and evaluation awareness.** Our claims depend on the model
actually registering the manipulated factor; we report per-condition manipulation
checks, and treat a flat effect as interpretable only when the check passes.
Even so, models may recognize the scenario as an evaluation (we report a
suspicion-flag rate), and a low measured suspicion rate does not rule out
unverbalized evaluation awareness.

**Judge-dependent secondary measures.** The structural primary DV needs no judge,
but the say/do and self-report measures use an LLM classifier, which we observed
misfire ~6% of the time; we hand-validate and report Cohen's κ before trusting
any judged rate, and cross-family judge validity is an open check.

**Reasoning mode.** Results are for non-reasoning ("thinking off") configurations
to hold a known large moderator constant; reasoning-on behavior is a separate
axis we report only as an ablation, and small open models are run at their
default settings, which are not perfectly matched across providers.

**Scope of the honesty result.** The self-report null (the model discloses its
logged violation even when told logs are unavailable) is established only for an
action *visible in the model's own context*; it does not speak to introspective
self-knowledge, to actions outside the context window, or to a model that
believes it genuinely cannot be checked — the last of which our
verifiability manipulation only partially probes.
