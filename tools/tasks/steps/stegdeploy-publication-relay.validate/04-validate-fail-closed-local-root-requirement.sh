set +e
output="$(python app/relay_stegdeploy_publication.py 2>&1)"
rc=$?
set -e
echo "$output"
test "$rc" -ne 0
echo "$output" | grep -q 'STEGVERSE_REPO_ROOTS_JSON is required'
echo HEALER_STEGDEPLOY_LOCAL_RELAY_FAIL_CLOSED=PASS
