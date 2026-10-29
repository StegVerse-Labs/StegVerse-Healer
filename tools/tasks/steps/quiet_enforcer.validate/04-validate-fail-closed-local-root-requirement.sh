set +e
python app/audit_schedules.py >/tmp/quiet.out 2>/tmp/quiet.err
rc=$?
set -e
cat /tmp/quiet.err
test "$rc" -ne 0
grep -q "STEGVERSE_REPO_ROOTS_JSON is required" /tmp/quiet.err
echo HEALER_QUIET_ENFORCER_FAIL_CLOSED=PASS
