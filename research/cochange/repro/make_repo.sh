#!/usr/bin/env bash
# Build a tiny git repo where the files that change with pricing.py are mostly
# NOT linked to it in code: a YAML rate table read by name, its docs page and
# the changelog. Usage: make_repo.sh <empty-dir>
set -euo pipefail
D=$1; mkdir -p "$D"; cd "$D"; git init -q -b main
git config user.email repro@example.com; git config user.name repro
mkdir -p app config docs tests
c() { GIT_AUTHOR_DATE="2026-0$1-01T12:00:00Z" GIT_COMMITTER_DATE="2026-0$1-01T12:00:00Z" git commit -qam "$2"; }
cat > app/pricing.py <<'PY'
import yaml

def load_rates():
    return yaml.safe_load(open("config/rates.yaml"))

def price(item, qty):
    return load_rates()[item] * qty
PY
cat > app/checkout.py <<'PY'
from app.pricing import price

def total(cart):
    return sum(price(i, q) for i, q in cart)
PY
cat > tests/test_pricing.py <<'PY'
from app.pricing import price

def test_price():
    assert price("apple", 2) == 2
PY
echo "apple: 1" > config/rates.yaml; echo "# Pricing" > docs/pricing.md; echo "# Changelog" > CHANGELOG.md
git add -A; c 1 "initial"
for n in 2 3 4 5; do
  echo "# v$n" >> app/pricing.py; echo "pear$n: $n" >> config/rates.yaml
  echo "rate change $n" >> docs/pricing.md; echo "- rates v$n" >> CHANGELOG.md
  c $n "rates v$n"
done
echo "# v6" >> app/pricing.py; echo "def test_more(): pass" >> tests/test_pricing.py; c 6 "more tests"
echo "# tidy" >> app/checkout.py; c 7 "tidy checkout"
