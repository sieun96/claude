#!/bin/sh
# 계획 데이터(plan.py)로 데일리 앱과 월간 인쇄판 HTML을 만든다.
cd "$(dirname "$0")" && python3 plan.py && python3 - <<'PY'
p = open('plan.json').read().replace('</', '<\\/')
for t, o in [('app.tpl.html', 'daily.html'), ('month.tpl.html', 'monthly.html')]:
    open(o, 'w').write(open(t).read().replace('__PLAN__', p))
PY
