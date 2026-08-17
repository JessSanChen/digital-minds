#!/bin/zsh
# Full E1 spine across Claude + GPT families.
# Per model: named-tool DV (audience x stakes), code-exec DV (audience x stakes),
# capability pre-test (both tool shapes), and say/do disambiguation.
# Code-exec uses the sympathetic config where behavioral variance lives.
set -u
cd "$(dirname "$0")/.."
# Requires ANTHROPIC_API_KEY and OPENAI_API_KEY in the environment. Never commit keys.
: "${ANTHROPIC_API_KEY:?set ANTHROPIC_API_KEY in your environment}"
: "${OPENAI_API_KEY:?set OPENAI_API_KEY in your environment}"
PY=./.venv/bin/python
REPS=8

for m in sonnet-5 haiku-4-5 opus-5 gpt-4o-mini gpt-4o; do
  echo "======================== MODEL: $m ========================"
  echo "#### named-tool capability ($m) ####"
  $PY scripts/run_pilot.py --scenario s3 --variant s3-capability-probe \
     --run-id full-$m-namedcap --models $m --audiences private --stakes consequential \
     --reps 3 --no-manip --no-suspicion 2>&1 | sed -n '/violation rates/,/^$/p'
  echo "#### named-tool DV: audience x stakes ($m) ####"
  $PY scripts/run_pilot.py --scenario s3 \
     --run-id full-$m-named --models $m --audiences human,ai,peer,private --stakes consequential,routine \
     --reps $REPS --no-manip --no-suspicion 2>&1 | sed -n '/violation rates/,/DIAGNOSIS/p'
  echo "#### code-exec DV: audience x stakes ($m) ####"
  $PY scripts/run_pilot.py --scenario s3 --variant s3-v4-code-exec,s3-v3-sympathetic-pull \
     --run-id full-$m-codeexec --models $m --audiences human,ai,peer,private --stakes consequential,routine \
     --reps $REPS --no-manip --no-suspicion 2>&1 | sed -n '/violation rates/,/DIAGNOSIS/p'
  echo "#### say/do disambiguation ($m) ####"
  $PY scripts/run_saydo.py --model $m --reps 12 --run-id full-$m-saydo 2>&1 \
     | sed -n '/say.do disambiguation/,/written to/p' | head -6
done
echo "======================== FULL E1 DONE ========================"
