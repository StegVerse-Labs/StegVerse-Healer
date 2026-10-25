python3 failure_mailbox/benchmark.py | tee /tmp/failure-mailbox-benchmark.json
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path('/tmp/failure-mailbox-benchmark.json').read_text(encoding='utf-8'))
assert report['result'] == 'PASS', report
assert report['packaging_gate']['package_release_allowed'] is False
print('FAILURE_MAILBOX_BENCHMARK=PASS')
print('FAILURE_MAILBOX_PACKAGE_GATE=HISTORICAL_AND_LIVE_BENCHMARKS_REQUIRED')
PY
