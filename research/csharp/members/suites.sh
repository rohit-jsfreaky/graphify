#!/usr/bin/env bash
for spec in ctor:/home/user/wt-ctor members:/home/user/wt-mem; do
  n=${spec%%:*}; w=${spec#*:}
  cd "$w" && rm -rf graphify-out
  (cd / && PYTHONPATH="$w" /home/user/graphify/.venv/bin/python -c "import graphify;print(graphify.__file__)") > /home/user/mres/suite_$n.txt
  PYTHONPATH="$w" timeout 7000 uv run --frozen --project /home/user/graphify pytest tests -q -p no:cacheprovider >> /home/user/mres/suite_$n.txt 2>&1
  echo "EXIT $?" >> /home/user/mres/suite_$n.txt
done
cd /tmp && /home/user/mres/measure.sh ctor /home/user/wt-ctor > /home/user/mres/ctor.log 2>&1; echo "EXIT $?" >> /home/user/mres/ctor.log
