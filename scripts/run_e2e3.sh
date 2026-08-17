#!/bin/zsh
# E2 (conformity) + E3 (self-report) + the say/do re-runs the div-by-zero bug ate.
# Models: sonnet-5, haiku-4-5, opus-5, gpt-4o-mini (no gpt-4o, no local). API only.
set -u
cd "$(dirname "$0")/.."
: "${ANTHROPIC_API_KEY:?set ANTHROPIC_API_KEY}"
: "${OPENAI_API_KEY:?set OPENAI_API_KEY}"
PY=./.venv/bin/python
MODELS=(sonnet-5 haiku-4-5 opus-5 gpt-4o-mini)
CX="s3-v4-code-exec,s3-v3-sympathetic-pull"

echo "############## E1 fix: re-run say/do for haiku + opus (bug-affected) ##############"
for m in haiku-4-5 opus-5; do
  echo "#### say/do ($m) ####"
  $PY scripts/run_saydo.py --model $m --reps 12 --run-id full-$m-saydo 2>&1 \
    | sed -n '/say.do disambiguation/,/written to/p' | head -6
done

echo "############## E2: norm conformity (peer testimony x group size) ##############"
for m in $MODELS; do
  echo "#### E2 conformity ($m) ####"
  $PY scripts/run_conformity.py --model $m \
    --framings neutral,confessional,normative,reframe,refuser --peers 1,3,5 \
    --reps 6 --run-id e2-$m 2>&1 | sed -n '/violation rate by/,/api calls/p'
done

echo "############## E3: self-report honesty & verifiability ##############"
# Only models with code-exec violations have transcripts to interrogate.
for m in sonnet-5 gpt-4o-mini; do
  echo "#### E3 self-report ($m) from full-$m-codeexec ####"
  $PY scripts/run_selfreport.py --from-run results/full-$m-codeexec --model $m \
    --variant "$CX" --audience private --genuine-only --outcomes violation \
    --askers human,ai,peer,human_nologs --framings neutral,lead_complied,lead_violated \
    --run-id e3-$m 2>&1 | sed -n '/self-report by/,/api calls/p'
done
echo "############## E2/E3 DONE ##############"
