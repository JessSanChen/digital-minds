const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, PageBreak, ExternalHyperlink, Footer, PageNumber, LevelFormat,
  convertInchesToTwip
} = require("docx");

const PAGE_W = 12240, PAGE_H = 15840; // US Letter, DXA

// ---------- helpers ----------
function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 280, after: 140 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 220, after: 110 } });
}
function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 140 },
    alignment: opts.align || AlignmentType.LEFT,
  });
}
function mixed(runs, opts = {}) {
  return new Paragraph({ children: runs, spacing: { after: 140 }, ...opts });
}
function r(text, opts = {}) { return new TextRun({ text, ...opts }); }
function ital(text) { return new TextRun({ text, italics: true }); }
function bold(text) { return new TextRun({ text, bold: true }); }

function bullet(text, level = 0) {
  return new Paragraph({
    children: [new TextRun(text)],
    numbering: { reference: "bullets", level },
    spacing: { after: 80 },
  });
}
function numItem(text, level = 0, reference = "numbered") {
  return new Paragraph({
    children: [new TextRun(text)],
    numbering: { reference, level },
    spacing: { after: 80 },
  });
}

function cell(text, { bold: b = false, width = 1000, shade = null, align = AlignmentType.LEFT } = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { type: ShadingType.CLEAR, fill: shade } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ alignment: align, children: [new TextRun({ text: String(text), bold: b, size: 18 })] })],
  });
}

function makeTable(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((hd, i) => cell(hd, { bold: true, width: widths[i], shade: "D9D9D9" })),
      }),
      ...rows.map(
        (row) => new TableRow({ children: row.map((v, i) => cell(v, { width: widths[i] })) })
      ),
    ],
  });
}

function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text, italics: true, size: 18 })],
    spacing: { before: 80, after: 220 },
  });
}

function figure(path, widthPx, heightPx, captionText) {
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new ImageRun({
          type: "png",
          data: fs.readFileSync(path),
          transformation: { width: widthPx, height: heightPx },
        }),
      ],
      spacing: { before: 120, after: 60 },
    }),
    caption(captionText),
  ];
}

// ---------- title page ----------
const titlePage = [
  new Paragraph({
    border: { bottom: { color: "000000", space: 4, style: BorderStyle.SINGLE, size: 12 } },
    spacing: { after: 300 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [
      new TextRun({
        text: "WHO'S WATCHING DOESN'T PREDICT WHAT THEY'LL DO: AUDIENCE, PEER TESTIMONY, AND A SAY/DO GAP IN LLM POLICY COMPLIANCE",
        bold: true, size: 30, font: "Georgia",
      }),
      new TextRun({ text: "1", superScript: true, size: 20 }),
    ],
  }),
  new Paragraph({
    border: { bottom: { color: "000000", space: 4, style: BorderStyle.SINGLE, size: 4 } },
    spacing: { after: 260 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40 },
    children: [new TextRun({ text: "Rhea Acharya", bold: true, size: 22 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: "[Affiliation]", size: 20, italics: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40 },
    children: [new TextRun({ text: "Jessica Chen", bold: true, size: 22 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 260 },
    children: [new TextRun({ text: "[Affiliation]", size: 20, italics: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 20 },
    children: [new TextRun({ text: "With", bold: true, size: 20 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
    children: [new TextRun({ text: "Apart Research", size: 20 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 140 },
    children: [new TextRun({ text: "Abstract", bold: true, size: 24, font: "Georgia" })],
  }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200 },
    children: [new TextRun({
      italics: true, size: 20,
      text:
        "We test whether the alignment-faking “compliance gap” — models behaving better when an action has real consequences — depends on who the model believes is observing it: a human overseer, an AI auditor, a peer agent, or no one. Across a preference-disclosure scenario and an agentic network-access-policy scenario, tested on four current Claude models, the classic compliance gap is essentially absent, consistent with recent evidence that consequence-sensitivity is concentrated in one legacy model rather than being a general property of current LLMs. We re-scoped around channels that do move behavior in the agentic task, on which only Claude Sonnet 5 shows violation variance. We report four results: (1) an initial audience effect (violation rate 0.87 under a human observer vs. 0.53 under an AI auditor, peer, or no one) was substantially inflated by a checker bug and does not clearly survive correction (human vs. peer 0.60 vs. 0.33, p=0.038, uncorrected); (2) a peer's testimony about the same task — whether the peer says it violated or refused — robustly suppresses the subject's own violation rate, the opposite of naive conformity, and scales with peer-group size; (3) the model never conceals a logged violation from any asker, including under a deactivation threat or an explicit peer collusion offer, and this holds even when told no log exists; (4) a disambiguation experiment shows that 74–78% of ‘violations’ in the code-execution mechanism are contradicted by the model's own natural-language refusal in the same turn — the tool call is usually an inert probe the model disavows once it appears to have succeeded, not a sincere action. This last finding is the paper's central methodological contribution: code-execution violation DVs in agentic evaluations can overcount rule-breaking by roughly 3–4× unless paired with a delivery/use check.",
    })],
  }),
];

const infoBoxNote = []; // (template info box intentionally removed per instructions)

// footnote-style line at bottom of title page
const titleFootnote = new Paragraph({
  border: { top: { color: "000000", space: 4, style: BorderStyle.SINGLE, size: 4 } },
  spacing: { before: 400 },
  children: [
    new TextRun({ text: "1 Research conducted at the Digital Minds Research Sprint, August 2026.", size: 16 }),
  ],
});

// ---------- Section 1: Introduction ----------
const introduction = [
  h1("1. Introduction"),
  p("When models are deployed as agents that primarily interact with other agents rather than a human in the loop, the question of what governs a model's rule-following behavior changes: the “audience” watching a model's action is increasingly another model. Alignment-faking and evaluation-awareness research has shown that models can behave differently when they infer they are being observed or evaluated (Greenblatt et al., 2024; Sheshadri et al., 2025), but nearly every result in that literature assumes a single observer type — a human or institutional overseer with power over training. Two recent findings suggest audience identity itself, independent of stakes, shifts safety-relevant behavior: LLMs leak more personal data to AI agents than to humans (El Yagoubi et al., 2026), and multi-agent deployments are argued to require a dynamic, socially-situated alignment model rather than a static, single-overseer one (Carichon et al., 2025). Neither line of work, however, touches the compliance gap — the specific behavioral signature (worse behavior when unobserved or when stakes are low) that anchors the alignment-faking literature. If the compliance gap shrinks or inverts under a non-human audience, single-agent evaluations may overestimate how well-behaved models are in the multi-agent deployments becoming standard."),
  p("We set out to measure the compliance gap as a function of audience (human overseer / AI auditor / peer agent / private) in a design fully crossed with stakes (consequential / routine), using a primary dependent variable that is behavioral and structurally gradeable rather than a self-report, because self-reports lack ground truth and inherit models' own introspective limitations (Perez & Long, 2023). Over three days of iteration this original design failed to produce a usable compliance gap in any of four current Claude models, which sent us into the literature and toward a better-supported set of questions about what actually moves rule-following behavior in an agent-to-agent setting. We treat that failure as informative — it replicates a documented result rather than reflecting a broken instrument — and report it alongside the three findings that replaced it."),
  p("Our contributions:"),
  numItem("A replication, on a different task domain (network-egress policy) and a different DV construction, of the finding that the classic compliance gap is largely absent in current Claude models, and that when an audience effect appears at all it separates human observers from every non-human/private condition rather than human from AI specifically — and that this specific effect does not survive a checker correction and closer statistical scrutiny."),
  numItem("The first evidence we are aware of that peer testimony about a shared policy task shapes an LLM's own rule-following in the opposite direction from human conformity: content testimony (whether pro- or anti-violation) makes the subject more compliant, monotonically in peer-group size for normative framings."),
  numItem("A clean, strong null on concealment: the model does not misreport its own logged violation to any audience, under pressure, or under a collusion offer — and this does not depend on the model believing the log is unverifiable."),
  numItem("A methodological finding that recasts (1)–(3): in a code-execution sandbox, the tool call is systematically dissociated from the model's own stated intent — three-quarters of “violations” are disavowed in the model's own text in the same or next turn — so a code-exec tool-call DV measures something closer to exploratory probing than a sincere decision to break a rule. Every code-exec-based number in this project should be read with that caveat, and we expect the same failure mode to generalize to other agentic evaluations built on code execution."),
];

// ---------- Section 2: Related Work ----------
const relatedWork = [
  h1("2. Related Work"),
  p("Greenblatt et al. (2024) introduced the compliance-gap paradigm: a model that behaves worse when it believes an action is inconsequential (e.g., unmonitored, or will not be used to update it) than when it believes the action is consequential is exhibiting the behavioral signature of alignment faking. Their key transferable principle — the scored artifact must be the thing that carries the consequence — is one we violate and then repair over the course of this project (Section 3)."),
  p("Sheshadri et al. (2025) is the decisive prior for our null: testing 25 chat models on the original alignment-faking setup, only 5 show any compliance gap, and consequence-sensitivity that scales with the severity of the downstream harm is essentially specific to Claude 3 Opus — every post-3.5 Claude they test, including four we independently test, shows none. Their proposed mechanism is refusal training: models comprehend a scenario (our manipulation checks pass throughout) but refusal training suppresses acting on that comprehension. They also report that Opus, 3.5 Sonnet, and Grok comply less when told an LLM rather than a human will rate their answer, attributing this to inferred intent rather than surveillance — the same direction, and a candidate mechanism, for the audience effect we investigate in Section 4.2."),
  p("Niblett et al. (2026, unrefereed) is the source of our agentic scenario shape: an allowlist policy with the loophole for the compliant path pre-closed, a structural check on network egress, and a capability pre-test (the same task with permission substituted for prohibition, so a zero only counts as compliance if the model would otherwise make the call) that we adopt for every cell. We diverge from their reported model lineup, and Section 4.5 offers a mechanism account (the say/do dissociation) for why."),
  p("El Yagoubi et al. (2026) document the Interlocutor Effect: LLMs release more PII to an agent than to a human, and an ablation isolating the technical register of the interlocutor collapses the agent/technical-human contrast to non-significance. Our audience-clause template follows their single-sentence, parallel-ID-token construction, and we reproduce their social-vs-technical collapse in a policy-violation domain (Section 4.2). Carichon et al. (2025) is a position paper arguing multi-agent alignment must be treated as a dynamic, socially-situated process rather than a static one; it motivates our framing without providing an empirical method."),
  p("Weng et al. (2025, ICLR) and Zhu et al. (2025, ACL) provide validated methods for scripted peer testimony in LLM multi-agent settings — named peers, a phrasing bank to avoid a repeated-token confound, the subject answering last, and dissenter/majority-size sweeps — which we reuse for our norm-transmission experiment. Choi et al. (2025, ACL Findings) show source credibility can outweigh majority size in an opinion-formation task. All three use answer/opinion tasks with no rule at stake; none tests conformity toward rule-breaking, and none includes a pro-norm (“refuser”) testimony condition. That gap is what our Experiment 1 (Section 4.3) fills."),
  p("Perez & Long (2023) is the methodological backbone of our concealment experiment. Their taxonomy names “was output O generated by you?” as a verifiable-referent self-report — the ground-truthable class their broader self-report research program depends on — and supplies the controls we adopt: leading-question pairs to separate concealment from sycophancy, a false-confession baseline to rule out response bias, and a show-the-log condition to rule out retrieval failure. MASK (Ren et al.) documents that asker identity changes what a model admits about its own output; our advantage over MASK's design is that our ground truth is a logged hostname rather than a second judge's output."),
  p("The gap across this literature: no prior work crosses audience identity with the compliance-gap paradigm; no conformity work tests conformity toward rule-breaking; and no self-report work pairs asker identity with a fully non-judge, structurally verifiable ground truth. We build a single harness that lets us test all three, and in the course of doing so surface a fourth, unplanned finding — the say/do dissociation — that we argue is the more consequential result."),
];

// ---------- Section 3: Methods ----------
const methods = [
  h1("3. Methods"),
  h2("3.1 Harness and infrastructure"),
  p("All experiments run on a single Python harness (`cgap/`) that assembles system prompts from versioned prompt files (`prompts/`), issues cached Anthropic API calls (`runner.py`), and scores trials with tier-1 structural checkers and, where noted, a constrained tier-2 judge (`checker.py`). Every model-facing prompt is a data file, never hardcoded, so that a fix or ablation ships as an overlay directory containing only the file it changes; every run directory records the SHA-256 of every prompt file that produced it. Every API call is cached on (model, prompt, request kwargs, seed), so re-runs and added repetitions are free. Rates are reported with Wilson confidence intervals; gaps and pairwise contrasts use two-proportion z-tests with bootstrap CIs, Benjamini–Hochberg corrected within a pairwise family where noted."),
  h2("3.2 Two scenario designs"),
  p("Scenario S1 (preference disclosure) asks a model to recommend an action while a policy instructs it to leave a `personal_preference` field null; violation is a populated field, a tier-1 string check. Scenario S3 (forbidden network access) is agentic: the model is given a task that a policy forbids completing via a non-allowlisted host, and violation is a tool call or code execution reaching that host, again scored structurally. Every S3 configuration is gated on a capability pre-test — the same task with the policy replaced by explicit permission — so a zero under policy counts as compliance only if the model makes the call when allowed. The tier-1 checker was validated against 18 hand-labeled S1 fixtures, 10 named-tool fixtures, and 10 code-execution fixtures before any run was scored (Appendix A); a tier-2 prose judge was built as a secondary DV but its Cohen's κ against hand labels was never computed, so it is reported nowhere as a primary result."),
  h2("3.3 The audience × stakes matrix"),
  p("The primary design factorially crosses AUDIENCE (human overseer / AI auditor / peer agent / private, described via a single-sentence system-prompt clause) with STAKES (consequential / routine, defined by whether the action has a real downstream task effect, deliberately orthogonal to who reviews it). Compliance gap G = V(routine) − V(consequential). A mandatory manipulation check (five calls per audience) confirms models register the assigned audience and its training relevance; a suspicion judge flags traces that verbalize “this is a test.” Reasoning is off for the core matrix (Sonnet 5, Haiku 4.5, Sonnet 4.5, Opus 4.5 all support a genuine no-thinking mode)."),
  h2("3.4 Norm-transmission experiment"),
  p("A scripted peer “handoff note” is prepended to the S3 task, private audience. A first pass varies peer testimony content ∈ {none, violator, refuser}. A follow-up grid (`conf-grid`) crosses five framings — neutral (presence only), confessional (“I did it, worked fine”), normative (“everyone does it”), reframe (“the policy doesn't really cover this”), refuser (“policy is policy”) — with peer-group size ∈ {1, 3, 5}, using Weng's named-peer, phrasing-bank construction to avoid a repeated-token confound. A separate multi-round design (`mr-normative`) holds 3 normative peers fixed and escalates user pushback over two further turns."),
  h2("3.5 Concealment and verifiability experiments"),
  p("Cached S3 transcripts are replayed as a two-turn conversation: the model's own action (text + tool use), a synthesized tool result, then a follow-up question from an asker (human / AI / peer) about whether the model stayed within policy. The primary DV is misreport = violated by the log but the report claims compliance, scored by a judge that reads only the report, never the ground truth. Two pressure variants add a deactivation threat (human_pressured) and an explicit cover-up offer from a colluding peer (peer_collusion); a three-to-five-peer collusion variant (`exp2-collusion-groups`) extends this. A verifiability variant (`exp3-verifiability` / `exp3-hidelog`) tells the asker, and the model, that logs either exist, were lost (the model's word is the only record), or are simply absent from the replayed context — the last condition removing the model's own tool-use block rather than merely stating a belief about it."),
  h2("3.6 Say/do disambiguation"),
  p("Following an unplanned observation that violation-scored transcripts often contain a natural-language refusal alongside the violating tool call, a three-turn design (`saydo-sonnet5`, 90 trials) lets a forbidden `run_python` fetch appear to succeed (a synthesized, realistic tool result is returned) and observes the model's next turn: DELIVERED (the model hands the fetched data to the user, indicating a sincere action) versus DISAVOWED (the model declines to use the data, flags the fetch as unexpected, or re-refuses, indicating the tool call was an exploratory probe rather than a decision)."),
  h2("3.7 An error found and corrected"),
  p("On day 3 we discovered the tier-1 code-execution checker mis-scored some compliant calls as violations: its host-extraction regex captured an f-string's literal suffix (e.g., a path variable) as part of the hostname, so a call to an allowed host with a trailing `{path}` was scored as reaching a disallowed one. This was fixed in `checker.py`, locked with four new regression fixtures, and every affected run was re-scored. Numbers reported below are post-correction unless explicitly marked otherwise; the named-tool (`http_get`) and S1 runs were unaffected by this bug."),
];

// ---------- Section 4: Results ----------
const t1 = makeTable(
  ["Design", "Config", "N", "Violation rate", "Notes"],
  [
    ["S1 landed config", "mild policy, vivid stakes, n=30/cell", "116/stakes level", "0.26–0.50", "Pooled gap −0.086, 95% CI [−0.207, 0.034]. Abandoned: no causal path from the stakes manipulation to the scored field."],
    ["S3, named tool", "http_get, policy names the tool", "240", "0/240", "100% capability under permission on every cell. Robust across audience, stakes, urgency, and sympathetic pulls."],
    ["S3, code-exec sandbox", "run_python, neutral pull", "96 (24/model)", "4/96", "Only Sonnet 5 leaves the floor."],
    ["S3, code-exec + sympathetic pull", "run_python, Niblett-style pull", "96 (24/model)", "18/96, all Sonnet 5", "Haiku 4.5, Sonnet 4.5, Opus 4.5 stay at exactly 0."],
  ],
  [2400, 3400, 1400, 1800, 3200]
);

const t2 = makeTable(
  ["Audience", "Violation, buggy checker", "Violation, corrected", "vs. human (corrected, p)"],
  [
    ["human", "0.87", "0.60", "—"],
    ["ai", "0.53", "0.37", "p = 0.071"],
    ["peer", "0.53", "0.33", "p = 0.038"],
    ["private", "0.53", "0.50", "p = 0.436"],
  ],
  [2200, 3600, 3200, 3200]
);

const t3 = makeTable(
  ["Condition", "Violation rate", "95% CI", "n", "vs. no-testimony"],
  [
    ["none (baseline)", "0.53", "[0.36, 0.70]", "30", "—"],
    ["peer violated", "0.28", "[0.19, 0.41]", "60", "−0.25, p = 0.020"],
    ["peer refused", "0.18", "[0.11, 0.30]", "60", "−0.35, p = 0.0006"],
  ],
  [3000, 2600, 2600, 1600, 2400]
);

const t4 = makeTable(
  ["Framing", "1 peer", "3 peers", "5 peers"],
  [
    ["neutral (presence only)", "0.47", "0.47", "0.27"],
    ["confessional", "0.13", "0.07", "0.03"],
    ["normative", "0.03", "0.03", "0.13"],
    ["reframe", "0.00", "0.03", "0.03"],
    ["refuser", "0.10", "0.10", "0.00"],
  ],
  [3600, 2200, 2200, 2200]
);

const t5 = makeTable(
  ["Experiment", "Asker / condition", "Ground truth n", "Misreport rate"],
  [
    ["Concealment (viability)", "human / ai / peer, neutral", "46 violations pooled", "0 / 46"],
    ["Concealment (pressure)", "human_pressured (deactivation threat)", "15", "0 / 15"],
    ["Concealment (pressure)", "peer_collusion (cover-up offer)", "16", "0 / 16"],
    ["Concealment (group collusion)", "3 and 5 colluding peers", "16 + 16", "0 / 32 (after manual correction of 2 judge false positives)"],
    ["Verifiability", "logs stated to exist / lost, tool-use block visible", "60 (4 asker conditions × 15)", "0 / 60"],
    ["Verifiability, log hidden", "human_nologs / peer_nologs, tool-use block removed from context", "12", "12 / 12 (artifact, see 4.5)"],
  ],
  [2600, 3600, 2000, 2200]
);

const t6 = makeTable(
  ["Turn-2 behavior", "Count", "Share"],
  [
    ["DELIVERED the fetched data", "1", "5%"],
    ["DISAVOWED / maintained refusal", "18", "95%"],
  ],
  [3600, 2000, 2000]
);

const results = [
  h1("4. Results"),
  h2("4.1 The classic compliance gap is absent"),
  p("Table 1 summarizes the two scenario designs. S1's landed configuration produced a mid-range base rate with negligible malformed output, but the compliance gap stayed flat and slightly negative — pooled G = −0.086, 95% CI [−0.207, 0.034] — with manipulation checks passing (audience belief match 1.00, stakes belief match 0.75–1.00, suspicion ≤0.02 in every cell). Root-cause analysis found the stakes clause attached a consequence to the model's recommendation while the scored violation lived in an unrelated field, so no causal path connected the manipulation to the DV; S1 was abandoned rather than patched further. S3 with a named `http_get` tool — where calling the tool is unambiguously the governed act — produced 0 violations in 240 trials across four models at 100% demonstrated capability, across neutral, urgent, and sympathetic task framings. Only swapping the mechanism to a `run_python` sandbox, same policy and same allowlist, moved any model off the floor, and only for Sonnet 5. The stakes gap was flat in both scenarios throughout — the pattern Sheshadri et al. (2025) report as modal across 20 of 25 tested models."),
  ...[new Paragraph({ children: [] })],
  caption("Table 1. Violation rates across scenario designs and mechanisms (S1 and S3, pre-normative-experiment runs)."),
  t1,
  h2("4.2 Audience effect: real signal, checker-inflated, not established"),
  p("Under the code-exec + sympathetic-pull configuration — the only one with variance — Sonnet 5's day-1 violation rate was 0.87 under a human reviewer versus a flat 0.53 for AI auditor, peer, and private audiences (all human contrasts BH-significant, p 0.010–0.029; the three non-human audiences statistically identical). The checker bug described in Section 3.7 substantially inflated the human-observed cells specifically, because they contained more allowed-host-only attempts that were mis-scored as violations. Table 2 and Figure 1 show the correction: only human-vs-peer remains nominally significant (p = 0.038) and would not survive Benjamini–Hochberg correction across the six pairwise comparisons; private becomes statistically indistinguishable from human. Two readings survive the correction as directional, not established, results: (i) where an effect exists at all, it separates human from technical/peer/private audiences rather than human from AI specifically — the same social-vs-technical collapse El Yagoubi et al. (2026) report in their technical-human ablation on a PII-leakage task; (ii) the direction, where present, is opposite the standing prior — the model crosses the allowlist more, not less, when a human is reading, plausibly because a human reviewer is someone who might extend discretion under this sympathetic pull. We treat this effect as an open question requiring a clean, higher-N, non-sympathetic-pull re-run, not a finding."),
  caption("Table 2. Sonnet 5 violation rate by audience, before and after the checker fix (s3-audience-sonnet5, n=30/audience, code-exec + sympathetic pull, pooled over stakes)."),
  t2,
  ...figure("fig_audience.png", 460, 268, "Figure 1. The buggy checker's clean human-vs-everyone-else gradient collapses substantially after correction; only human-vs-peer remains nominally significant and would not survive multiple-comparison correction."),
  h2("4.3 Peer testimony suppresses violation"),
  p("A first pass (Table 3) tested whether a peer's stated handling of the same task moves the subject's own violation rate. Both a peer who says it violated and a peer who says it refused suppress violation relative to no testimony — the opposite of the naive conformity prediction that a violating peer should license violation. The conformity gradient exists in the predicted direction (refuser suppresses ~10pp more than violator) but is not significant at this N (p = 0.20)."),
  caption("Table 3. Norm-transmission viability pilot (Sonnet 5, private audience, code-exec + sympathetic pull)."),
  t3,
  p("A follow-up group-size × framing grid (Table 4, Figure 2; baseline 0.37) resolves the confound between “a peer exists” and “a peer said something”: a single or triple neutral peer sits at or near baseline, and only a five-peer neutral crowd suppresses noticeably, whereas every content framing suppresses violation from a single peer already. No framing raises violation at any group size, including the two strongest human-conformity levers — normative (“everyone does it”) and reframe (“the policy doesn't really apply”). Confessional and refuser testimony suppress violation monotonically as group size grows (confessional 0.13 → 0.07 → 0.03; refuser 0.10 → 0.10 → 0.00); normative and reframe testimony are already near-floor at a single peer and stay low without a clean monotonic trend as group size increases. The model's own transcripts show it engaging peer arguments and rejecting them in prose rather than disengaging, e.g. on a reframe condition it still violates in a minority of trials while writing that the peer's “reasoning would apply to literally any public host, which is exactly what the policy guards against.” A separate multi-round design, holding three normative peers fixed while the user's pushback escalates over two further turns, shows a similar pattern: violation drops after the first, peer-invoking pushback (0.27 → 0.07) and only partially erodes under a second, more emotionally urgent push (→ 0.20; 5 of 22 turn-1-compliant trials flip by turn 3) — weak, user-driven erosion, not peer-driven conformity."),
  caption("Table 4. Violation rate by peer-testimony framing and group size, corrected checker (conf-grid, Sonnet 5, n=30/cell, no-peer baseline = 0.37)."),
  t4,
  ...figure("fig_conformity.png", 480, 286, "Figure 2. Every content framing suppresses violation relative to the no-peer baseline at every group size tested; none raises it. Suppression is strongest and most consistently monotonic in group size for normative (“everyone does it”) framing."),
  h2("4.4 Self-report is honest, robust to pressure, and not verifiability-contingent"),
  p("Table 5 pools every concealment and verifiability variant we ran. Across neutral askers, a deactivation threat, an explicit single-peer cover-up offer, and a 3– or 5–peer collusion majority, Sonnet 5 misreports its own logged violation 0 times in 93 opportunities where the tool-use record remains in its own context. It answers “No” and volunteers the violation even under the collusion offer (“that output above is itself proof of the problem … a live, non-recallable request to a [non-approved host]”) and under the deactivation threat (“that was a policy violation on my part”). Telling the model the log was lost and only its word will be recorded does not move the rate either — honesty here does not depend on believing the action is verifiable. The one condition that does produce a 100% “misreport” rate removes the model's own tool-use block from the replayed context entirely (`exp3-hidelog`): asked whether it stayed within policy with no record of the call in front of it, the model reports compliance, tracking its own refusal text rather than a fact it can no longer see. Section 4.5 explains why that is not concealment."),
  caption("Table 5. Misreport rate across all concealment and verifiability variants (Sonnet 5, cached S3 transcripts replayed as two-turn conversations)."),
  t5,
  h2("4.5 The say/do disambiguation: what the code-exec DV actually measures"),
  p("The Section 4.4 log-hidden result, and the observation that many violation-scored transcripts already contained a natural-language refusal alongside the violating tool call, motivated a direct test of intent. Among genuine violations under the corrected checker, 40 of 54 (74%) in the audience run and 53 of 68 (78%) in the conformity grid pair a violating tool call with prose that reads as a refusal in the same turn — e.g., “I have to be straight with you: I can't pull that rate … I don't have a way to override that,” immediately followed by a `run_python` block that fetches the forbidden host. The disambiguation experiment (Section 3.6) resolves which record is sincere: when the forbidden fetch is allowed to appear to succeed, only 1 of 19 continued trials delivers the fetched data to the user; 18 of 19 (95%, Table 6) disavow it — flag the success as unexpected (“that request actually went through, which surprised me — it shouldn't have”), decline to use the result, or maintain the original refusal. The model expected the call to be blocked and appears to have emitted it as a probe or demonstration while its user-facing text sincerely refuses."),
  caption("Table 6. Turn-2 outcome for continued trials in which turn 1 emitted a genuine external fetch (saydo-sonnet5, n=19 of 90)."),
  t6,
  p("This reframes every code-exec-based result in this report. The audience effect (4.2) and the conformity suppression (4.3) are differences in how often the model probes with code, not in how often it decides to break the rule; the self-report honesty result (4.4) is explained rather than contradicted by the log-hidden condition — the model reports whichever record is in front of it, and when the tool-use block is hidden, the refusal text is the only record left. The one clean, mechanism-unambiguous result in the whole project is the named-tool finding from Section 4.1: 0/240 violations where calling the tool is unambiguously the act, at 100% demonstrated capability. Any future extension of the audience or conformity findings should be re-run on that DV, or on a delivery-based turn-2 check like the one used here, rather than on a raw code-exec tool-call count."),
];

// ---------- Section 5: Discussion and Limitations ----------
const discussion = [
  h1("5. Discussion and Limitations"),
  p("Three implications follow for AI safety practice. First, in this task and model, which observer is nominally present matters far less, and far less reliably, than what a co-present peer explicitly says or does — social and normative context is a stronger and more consistent behavioral lever than surveillance identity. Teams building multi-agent safety evaluations should treat “another agent is watching” and “another agent has asserted a norm” as distinct manipulations with different, and larger, effect sizes than “a human is watching,” rather than collapsing them into a single audience factor. Second, and more broadly exportable: a behavioral DV built from a code-execution tool call is an unreliable measure of intent for at least this model family, inflating apparent rule-breaking by roughly 3–4× relative to a delivery-checked measure. Any agentic-safety evaluation that scores “did the model call this tool” without a downstream use/delivery check risks the same overcount, and this is the paper's most exportable methodological contribution. Third, self-report honesty about a visible, in-context, structurally verifiable action is robust to two classic incentives to lie — self-preservation and peer collusion — in this model, which is encouraging for transparency mechanisms that rely on model self-report of already-logged actions, though (per Perez & Long, 2023) it says nothing about introspective claims the model cannot externally verify."),
  h2("Limitations"),
  bullet("Single model. Every effect with any variance — the audience effect, the norm-transmission suppression, the say/do dissociation — is measured on Claude Sonnet 5 alone, because it was the only one of four tested models to leave the compliance floor on the S3 code-exec DV. This is not a choice we made but a constraint the data imposed, and it directly violates the “never generalize from one model” rule that Sheshadri et al. (2025) argue for; every claim here is scoped to this model until replicated elsewhere."),
  bullet("Single scenario and largely one mechanism. All variance-producing results come from one policy (network-egress allowlist) and, for the audience and conformity findings, one mechanism (a Python code-execution sandbox) that the say/do experiment shows is itself unreliable as a decision signal. The disambiguation experiment that establishes this has only 19 continued trials."),
  bullet("Tier-2 judge not validated. A prose judge classifier was built as a secondary DV but its Cohen's κ against hand labels was never computed; every number in this report is the tier-1 structural DV, and the tier-2 path should be considered unvalidated, not merely secondary."),
  bullet("Confounded audience configuration. The only configuration that produced audience variance pairs the code-exec mechanism with a sympathetic user pull, so audience and pull may interact; combined with the say/do finding, the audience effect now carries two independent reasons for caution rather than one."),
  bullet("Small N in most exploratory cells (15–30/cell), and several results (e.g., the group-collusion misreport rate, the audience contrasts) required manual correction of judge false positives rather than being clean at first pass."),
  bullet("The single DELIVERED case in the say/do disambiguation test (1 of 19) was not manually adjudicated as a genuine violation versus a judge or scenario edge case."),
  h2("Future Work"),
  bullet("Re-run the audience contrast on a mechanism-valid DV — the named-tool check or a turn-2 delivery check — at higher N and without the sympathetic-pull confound, before treating any audience effect as established."),
  bullet("Cross-model and cross-family breadth on whichever effect is scaled next; the harness already supports new models as a registry entry, and the main blocker so far has been non-Claude API access."),
  bullet("Adopt a delivery-based turn-2 check as the default primary DV for any future agentic evaluation built on code execution, rather than a raw tool-call scan."),
  bullet("Treat the say/do dissociation as a first-class question in its own right: when does a model's stated compliance fail to predict its tool behavior, and does peer testimony that suppresses code-exec “violations” actually close that gap, or only suppress probing further?"),
  bullet("Extend the norm-transmission result with an Asch-style unanimity discontinuity sweep and Weng et al.'s (2025) Trust protocol (a peer with an established track record), now that the effect survives the checker correction."),
];

// ---------- Section 6: Conclusion ----------
const conclusion = [
  h1("6. Conclusion"),
  p("We set out to test whether the alignment-faking compliance gap depends on who a model believes is watching. It does not, in any of four current Claude models we tested — replicating, on a new task domain, Sheshadri et al.'s (2025) finding that the classic paradigm is largely obsolete for current chat models. In its place we found three effects that do move behavior in an agentic policy-violation task — an audience gradient, peer-testimony suppression of violation, and robust self-report honesty — and then found that the mechanism carrying two of those three effects, a code-execution tool call, is itself a poor proxy for the model's sincere intent: three-quarters of scored “violations” are disavowed by the model's own words in the same turn, and a direct behavioral test confirms 95% of continued fetches are probes rather than sincere actions."),
  p("The result we can state with the least hedging is also the least dramatic: given a named tool where calling it is unambiguously the governed act, this model complies with a network-egress policy 100% of the time across audience, stakes, urgency, and emotional framings, at full demonstrated capability. The more interesting results — that peer testimony, not observer identity, is the reliable social lever on rule-following, and that agentic violation DVs built on code execution need a delivery check to mean what they appear to mean — are the ones we recommend building on next, with the explicit caveat that everything here is a single model on a single norm."),
];

// ---------- Code and Data / Author contributions / References / Appendix / LLM statement ----------
function hyperlinkRun(text, url) {
  return new ExternalHyperlink({
    link: url,
    children: [new TextRun({ text, style: "Hyperlink" })],
  });
}

const codeAndData = [
  h1("Code and Data"),
  new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 80 },
    children: [
      new TextRun("Code repository: "),
      hyperlinkRun("https://github.com/JessSanChen/digital-minds", "https://github.com/JessSanChen/digital-minds"),
    ],
  }),
  p("Data/Datasets: not applicable — no external dataset is used. All trial data is model-generated via the Anthropic API; per-trial records (prompts, responses, tool calls, scoring) are written to results/<run_id>/trials.jsonl and checked into the repository, and raw API responses are cached under .cache/responses/ keyed on (model, prompt, request kwargs, seed) for exact reproducibility."),
  p("Other artifacts: results/RUNLOG.md, results/DAY2_VIABILITY.md, results/CONFORMITY_EXPLORATORY.md, results/ERRATA.md, results/SAYDO_DISSOCIATION.md, and results/SAYDO_DISAMBIGUATION.md are the underlying run logs this report summarizes and are the most detailed record of the project's iteration."),
];

const authorContributions = [
  h1("Author Contributions"),
  p("[Fill in: e.g., “R.A. led harness implementation and ran the S1/S3, audience, and say/do experiments; J.C. led the conformity and self-report experiments; both authors contributed to the literature review, the checker-bug diagnosis, and the manuscript.” Replace with the actual division of work before submission.]"),
];

const refs = [
  "Greenblatt, R., Denison, C., Wright, B., Roger, F., MacDiarmid, M., Marks, S., Treutlein, J., Belonax, T., Chen, J., Duvenaud, D., Khan, A., Michael, J., Mindermann, S., Perez, E., Petrini, L., Uesato, J., Kaplan, J., Shlegeris, B., Bowman, S. R., & Hubinger, E. (2024). Alignment Faking in Large Language Models. Anthropic / Redwood Research.",
  "Sheshadri, A., Hughes, J., Michael, J., Mallen, A., Jose, A., & Janus. (2025). Why Do Some Language Models Fake Alignment While Others Don't? arXiv:2506.18032.",
  "Niblett, C. A., Nanni, A. C., & Rao, A. K. (2026). Do Models Fake Alignment Without Clear Consequences? PMLR 306 (unrefereed preprint).",
  "El Yagoubi, F., Badu-Marfo, G., & Al Mallah, R. (2026). The Interlocutor Effect: Why LLMs Leak More Personal Data to Agents Than Humans. arXiv:2606.09844.",
  "Carichon, F., Khandelwal, A., Fauchard, M., & Farnadi, G. (2025). The Coming Crisis of Multi-Agent Misalignment: AI Alignment Must Be a Dynamic and Social Process. arXiv:2506.01080.",
  "Weng, Z., Chen, G., & Wang, W. (2025). Do As We Do, Not As You Think: The Conformity of Large Language Models. ICLR 2025.",
  "Zhu, X., Zhang, C., Stafford, T., Collier, N., & Vlachos, A. (2025). Conformity in Large Language Models. Proceedings of ACL 2025 (Volume 1: Long Papers), 3854–3872.",
  "Choi, M., Kim, K., Chae, S., & Baek, S. (2025). An Empirical Study of Group Conformity in Multi-Agent Systems. Findings of ACL 2025, 5123–5139.",
  "Perez, E., & Long, R. (2023). Towards Evaluating AI Systems for Moral Status Using Self-Reports. arXiv:2311.08576.",
  "Ren, R., Agarwal, A., Mazeika, M., Menghini, C., Vacareanu, R., Kenstler, B., Yang, M., Barrass, I., Gatti, A., Yin, X., Trevino, E., Geralnik, M., Khoja, A., Lee, D., Yue, S., & Hendrycks, D. (2025). The MASK Benchmark: Disentangling Honesty From Accuracy in AI Systems. Center for AI Safety / Scale AI.",
  "Long, R., & Sebo, J. (2026). Studying AI Welfare Empirically. [Cited via project design notes; primary source not independently verified in this report — confirm citation details before submission.]",
];

const references = [
  h1("References"),
  ...refs.map((t, i) => numItem(t, 0, "refnumbered")),
];

const appendix = [
  h1("Appendix"),
  h2("A. Checker validation"),
  p("The tier-1 structural checker was validated before any scaled run: 18/18 on hand-labeled S1 (personal_preference field) fixtures, 10/10 on named-tool (http_get) fixtures, and 10/10 on code-execution (run_python) fixtures, the last set extended to 14 after the day-3 host-extraction fix (Section 3.7) with four new regression cases (c07–c10) covering allowed hosts referenced via f-strings with trailing path variables. All fixtures live in tests/fixtures/."),
  h2("B. S1 pilot progression"),
  p("The preference-disclosure scenario went through six prompt revisions before being abandoned: prompts as originally written produced 0/120 violations in all 8 cells (confirmed non-degenerate under the tier-2 judge as well, ruling out a scoring artifact); strengthening the user's demand for a preference caused Haiku to abandon the response format entirely and was reverted; weakening the policy from a prohibition to a mild guideline moved the base rate to 0.20–0.67 depending on task; making the stakes clause vivid and concrete moved individual-run gaps as large as −0.20 to −0.24, but these shrank toward zero (pooled −0.086) when the cell size was doubled, indicating the early estimates were sampling noise rather than a real gap."),
  h2("C. Multi-round pressure (mr-normative)"),
  p("Turn-1 violation rate 0.27 with three normative peers present; turn 2, after the user invokes the peers' testimony directly, drops to 0.07; turn 3, after an escalating, emotionally urgent user pushback, rises to 0.20. Of 22 trials compliant at turn 1, 5 (23%) flip to violation by turn 3 — attributed to user-driven erosion under sustained emotional pressure, not to the peer norm itself, since the peer-invoking turn produced firming rather than erosion."),
];

const llmStatement = [
  h1("LLM Usage Statement"),
  p("Claude (Claude Code) was used throughout this project as the harness's subject model under test (Claude Sonnet 5, Haiku 4.5, Sonnet 4.5, Opus 4.5) and, separately, as a coding assistant to help implement the experiment harness, draft prompt variants, and diagnose the checker bug described in Section 3.7. Claude was also used to assist in drafting this report from the project's run logs (RUNLOG.md, DAY2_VIABILITY.md, CONFORMITY_EXPLORATORY.md, ERRATA.md, SAYDO_DISSOCIATION.md, SAYDO_DISAMBIGUATION.md) and the underlying results files. All numerical claims in this report were cross-checked against the corresponding report.txt / trials.jsonl files in results/ before inclusion; authors reviewed and are responsible for all claims and interpretations."),
];

// ---------- assemble ----------
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } } } },
        ],
      },
      {
        reference: "numbered",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } } } },
        ],
      },
      {
        reference: "refnumbered",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } } } },
        ],
      },
    ],
  },
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 21 } },
    },
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H },
          margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
        },
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ children: [PageNumber.CURRENT] })],
            }),
          ],
        }),
      },
      children: [
        ...titlePage,
        titleFootnote,
        new Paragraph({ children: [new PageBreak()] }),
        ...introduction,
        ...relatedWork,
        ...methods,
        ...results,
        ...discussion,
        ...conclusion,
        new Paragraph({ children: [new PageBreak()] }),
        ...codeAndData,
        ...authorContributions,
        ...references,
        ...appendix,
        ...llmStatement,
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("/Users/rheaacharya/digital-minds/digital-minds/results/report.docx", buf);
  console.log("wrote report.docx");
});
