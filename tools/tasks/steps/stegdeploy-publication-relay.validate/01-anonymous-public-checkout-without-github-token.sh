set -euo pipefail
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
git config --global --unset-all http.https://github.com/.extraheader || true
git init .
git remote add origin https://github.com/StegVerse-Labs/StegVerse-Healer.git
if [ "${GITHUB_EVENT_NAME}" = "pull_request" ]; then
  SOURCE_REF="refs/pull/${PR_NUMBER}/merge"
else
  SOURCE_REF="${GITHUB_SHA}"
fi
env -u GITHUB_TOKEN -u GH_TOKEN git fetch --depth=1 origin "${SOURCE_REF}"
git checkout --detach FETCH_HEAD
