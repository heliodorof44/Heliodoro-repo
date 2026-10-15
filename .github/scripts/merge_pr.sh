#!/usr/bin/env bash
# Safer PR merge script
# Requires: gh (GitHub CLI) and jq
set -euo pipefail

REPO="${1:-Heliodoro-repo/snippets}"      # owner/repo, can be passed as first arg
BRANCH="${2:-contact-picker/loading-and-contract}"  # branch / PR head ref (second arg)
MERGE_METHOD="${3:-merge}"                # merge|squash|rebase
AUTO_YES="${AUTO_YES:-false}"             # set true to skip interactive confirmation

# helpers
die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "=> $*"; }

# ensure dependencies
command -v gh >/dev/null || die "gh (GitHub CLI) not found. Install from https://cli.github.com/"
command -v jq >/dev/null || die "jq not found. Install (e.g., apt-get install jq) or adjust script to use gh --jq."

# check gh auth
if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  die "gh is not authenticated. Run 'gh auth login' first."
fi

OWNER="${REPO%%/*}"
REPO_NAME="${REPO#*/}"

info "Fetching PR details for branch '$BRANCH' in repo '$REPO'..."
PR_JSON="$(gh pr view "$BRANCH" --repo "$REPO" --json number,title,url,mergeable,mergeStateStatus,state,isDraft,headRefOid || true)"
[ -n "$PR_JSON" ] || die "Failed to fetch PR details (no output). Is the branch/PR correct?"

PR_NUMBER="$(echo "$PR_JSON" | jq -r '.number // empty')"
PR_TITLE="$(echo "$PR_JSON" | jq -r '.title // empty')"
PR_URL="$(echo "$PR_JSON" | jq -r '.url // empty')"
PR_MERGABLE="$(echo "$PR_JSON" | jq -r '.mergeable // empty')"
PR_MERGESTATE="$(echo "$PR_JSON" | jq -r '.mergeStateStatus // empty')"
PR_STATE="$(echo "$PR_JSON" | jq -r '.state // empty')"
PR_IS_DRAFT="$(echo "$PR_JSON" | jq -r '.isDraft // false')"
HEAD_SHA="$(echo "$PR_JSON" | jq -r '.headRefOid // empty')"

if [ -z "$PR_NUMBER" ]; then
  die "No PR found for '$BRANCH' in $REPO (branch may not be a PR head)."
fi

cat <<-EOF

PR #$PR_NUMBER: $PR_TITLE
URL: $PR_URL
State: $PR_STATE
Draft: $PR_IS_DRAFT
Mergeable: $PR_MERGABLE
Merge state: $PR_MERGESTATE
Head commit: ${HEAD_SHA:-unknown}
EOF

# quick sanity checks
if [ "$PR_STATE" != "OPEN" ]; then
  die "PR is not open (state=$PR_STATE). Aborting."
fi

if [ "$PR_IS_DRAFT" = "true" ] || [ "$PR_IS_DRAFT" = "True" ]; then
  die "PR is a draft. Convert to ready for review before merging."
fi

# guard on mergeable/mergeStateStatus (tolerant)
if echo "$PR_MERGABLE" | grep -iq "CONFLICT"; then
  die "PR is reported as CONFLICTING. Resolve conflicts before merging."
fi

# prefer mergeStateStatus clean
if [ -n "$PR_MERGESTATE" ] && ! echo "$PR_MERGESTATE" | grep -iq "^clean$"; then
  echo "Warning: mergeStateStatus='$PR_MERGESTATE' (not 'clean'). Please inspect check runs and branch protection."
fi

# show check runs (try gh pr checks, fallback to check-runs API)
info "Checking CI / check runs for head commit..."
if gh pr checks "$BRANCH" --repo "$REPO" >/dev/null 2>&1; then
  gh pr checks "$BRANCH" --repo "$REPO"
else
  if [ -n "$HEAD_SHA" ]; then
    info "Using checks API for commit $HEAD_SHA"
    gh api -H "Accept: application/vnd.github+json" \
      "/repos/$OWNER/$REPO_NAME/commits/$HEAD_SHA/check-runs" \
      --jq '.check_runs[] | {name: .name, status: .status, conclusion: .conclusion}' || true
  else
    echo "Cannot determine head commit SHA; please inspect CI manually: $PR_URL"
  fi
fi

# interactive confirmation (or auto)
if [ "$AUTO_YES" != "true" ]; then
  read -rp "Proceed to merge PR #$PR_NUMBER into $REPO (method: $MERGE_METHOD)? (y/N) " CONFIRM
  if [ "${CONFIRM,,}" != "y" ]; then
    echo "Aborting merge."
    exit 0
  fi
fi

# perform merge
info "Merging PR #$PR_NUMBER (method=$MERGE_METHOD)..."
if gh pr merge "$PR_NUMBER" --repo "$REPO" --"$MERGE_METHOD" --delete-branch; then
  info "PR merged and branch deleted (if permitted)."
else
  die "gh pr merge failed. Inspect the PR: $PR_URL"
fi
