#!/usr/bin/env bash
# Input: --self-test only. Output: one pass/fail line.
# Writes: a temporary directory only. Network: none. Failure: exits non-zero.
set -euo pipefail

[[ "${1:-}" == "--self-test" && $# -eq 1 ]] || {
  echo "usage: $0 --self-test" >&2
  exit 2
}

tmp_dir="$(mktemp -d)"
cleanup() {
  rm -r -- "${tmp_dir}"
}
trap cleanup EXIT

repo="${tmp_dir}/repo"
mkdir "${repo}"
cd "${repo}"
git init -q
git config user.name "Wise Agent Fixture"
git config user.email "fixture@example.invalid"

printf '%s\n' "baseline target" >target.txt
printf '%s\n' "baseline unrelated" >unrelated.txt
printf '%s\n' \
  "target-old" "keep-1" "keep-2" "keep-3" "keep-4" "user-old" >overlap.txt
git add -- target.txt unrelated.txt overlap.txt
git commit -qm "baseline"

printf '%s\n' "staged unrelated change" >unrelated.txt
git add -- unrelated.txt
unrelated_before="$(git ls-files --stage -- unrelated.txt)"

printf '%s\n' "whitelisted target change" >target.txt
printf '%s\n' \
  "target-new" "keep-1" "keep-2" "keep-3" "keep-4" "user-new" >overlap.txt
candidate_index="${repo}/.git/candidate-index"
GIT_INDEX_FILE="${candidate_index}" git read-tree HEAD
GIT_INDEX_FILE="${candidate_index}" git add -- target.txt
printf '%s\n' \
  "target-new" "keep-1" "keep-2" "keep-3" "keep-4" "user-old" \
  >"${tmp_dir}/overlap-candidate.txt"
overlap_mode="$(git ls-tree HEAD -- overlap.txt | awk '{print $1}')"
overlap_blob="$(git hash-object -w "${tmp_dir}/overlap-candidate.txt")"
GIT_INDEX_FILE="${candidate_index}" git update-index \
  --add --cacheinfo "${overlap_mode},${overlap_blob},overlap.txt"
candidate_paths="$(GIT_INDEX_FILE="${candidate_index}" git diff --cached --name-only)"
[[ "${candidate_paths}" == $'overlap.txt\ntarget.txt' ]] || {
  echo "FAIL candidate index is not the whitelist: ${candidate_paths}" >&2
  exit 1
}

GIT_INDEX_FILE="${candidate_index}" git commit -qm "commit target only"
committed_paths="$(git diff-tree --no-commit-id --name-only -r HEAD)"
[[ "${committed_paths}" == $'overlap.txt\ntarget.txt' ]] || {
  echo "FAIL commit is not the whitelist: ${committed_paths}" >&2
  exit 1
}

read -r target_mode _ target_blob _ < <(git ls-tree HEAD -- target.txt)
git update-index --cacheinfo "${target_mode},${target_blob},target.txt"
read -r overlap_mode _ overlap_blob _ < <(git ls-tree HEAD -- overlap.txt)
git update-index --cacheinfo "${overlap_mode},${overlap_blob},overlap.txt"
unrelated_after="$(git ls-files --stage -- unrelated.txt)"
[[ "${unrelated_after}" == "${unrelated_before}" ]] || {
  echo "FAIL unrelated staged blob changed" >&2
  exit 1
}

[[ "$(git status --short -- overlap.txt)" == " M overlap.txt" ]] || {
  echo "FAIL same-file user change was not preserved" >&2
  exit 1
}
[[ "$(git status --short -- unrelated.txt)" == "M  unrelated.txt" ]] || {
  echo "FAIL unrelated staged change was not preserved" >&2
  exit 1
}

git commit -qm "commit preserved unrelated change"
next_commit_paths="$(git diff-tree --no-commit-id --name-only -r HEAD)"
[[ "${next_commit_paths}" == "unrelated.txt" ]] || {
  echo "FAIL real index is not reusable: ${next_commit_paths}" >&2
  exit 1
}

echo "OK dirty-worktree commit fixture"
