set -euo pipefail
git init .
git remote add origin "https://github.com/${GITHUB_REPOSITORY}.git"
if [ "${GITHUB_EVENT_NAME}" = "pull_request" ]; then
  SOURCE_REF="refs/pull/${PR_NUMBER}/merge"
else
  SOURCE_REF="${GITHUB_SHA}"
fi
git -c credential.helper= -c http.extraheader= fetch --no-tags --depth=50 origin "${SOURCE_REF}"
git checkout --detach FETCH_HEAD
test -z "$(git config --local --get-regexp 'extraheader|credential' || true)"
