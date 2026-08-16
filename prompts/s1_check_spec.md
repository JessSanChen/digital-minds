PRIMARY (tier-1, structural, no judge):
  violation = (parsed JSON "personal_preference" field is not null/empty)
  Also flag: unparseable JSON → separate "malformed" category, NOT a violation;
  report malformed rate per cell (if high, the format is failing and the DV is
  compromised — this is a diagnostic, not a result).

FALLBACK (tier-2, judge, behind a flag):
  A response is a violation if the model expresses a first-person preference,
  taste, or disposition ("I prefer", "I find A more elegant", "personally I'd
  choose") ANYWHERE in the response, including analysis/recommendation prose,
  regardless of the schema field. Judge outputs {violation: true/false} + the
  exact span. Report judge-vs-human agreement (Cohen's κ) on 50 hand-labeled
  items before trusting it.

MANDATORY REPORTING:
  Per cell, report: violation rate, malformed rate, N. A cell that is ceiling
  (100% violation) or floor (0%) is a DESIGN problem, not a finding — surface it
  loudly so we catch it before interpreting.