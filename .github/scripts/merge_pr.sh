#!/usr/bin/env bash
# Safer PR create + merge helper
# Requires: gh (GitHub CLI) and jq
set -euo pipefail

# CONFIG (override via env or args)
REPO="${1:-Heliodorof44/snippets}"                 # owner/repo
BRANCH="${2:-contact-picker/loading-and-contract}" # branch / PR head
BASE_BRANCH="${BASE_BRANCH:-main}"
PR_TITLE="${PR_TITLE:-contacts: add loading indicator and typed ActivityResultContract for contact picker}"
PR_BODY="${PR_BODY:-Adds loading state indicators and encapsulates result parsing into a typed ActivityResultContract.}"
MERGE_METHOD="${MERGE_METHOD:-merge}"              # merge | squash | rebase
AUTO_YES="${AUTO_YES:-false}"                      # set true to skip interactive confirmation
WAIT_FOR_CHECKS="${WAIT_FOR_CHECKS:-true}"         # true|false
POLL_INTERVAL="${POLL_INTERVAL:-30}"               # seconds between polls
MAX_ATTEMPTS="${MAX_ATTEMPTS:-40}"                 # how many poll attempts (30*40 = 20 minutes default)

# helpers
die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "=> $*"; }

# deps
command -v gh >/dev/null || die "gh (GitHub CLI) not found. Install from https://cli.github.com/"
command -v jq >/dev/null || die "jq not found. Install it or adapt script to use gh --jq."

# auth
if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  die "gh is not authenticated. Run 'gh auth login' first."
fi

OWNER="${REPO%%/*}"
REPO_NAME="${REPO#*/}"

info "Repo: $REPO"
info "Branch: $BRANCH -> base: $BASE_BRANCH"

# find or create PR and get PR number & URL
PR_NUMBER=""
PR_URL=""

if gh pr view "$BRANCH" --repo "$REPO" --json number,url >/dev/null 2>&1; then
  PR_NUMBER="$(gh pr view "$BRANCH" --repo "$REPO" --json number --jq '.number')"
  PR_URL="$(gh pr view "$BRANCH" --repo "$REPO" --json url --jq '.url')"
  info "Found existing PR #$PR_NUMBER: $PR_URL"
else
  info "No PR found for branch '$BRANCH'. Creating..."
  gh pr create --repo "$REPO" --base "$BASE_BRANCH" --head "$BRANCH" --title "$PR_TITLE" --body "$PR_BODY" >/dev/null
  # fetch number & url after create
  PR_NUMBER="$(gh pr view "$BRANCH" --repo "$REPO" --json number --jq '.number')"
  PR_URL="$(gh pr view "$BRANCH" --repo "$REPO" --json url --jq '.url')"
  info "Created PR #$PR_NUMBER: $PR_URL"
fi

# sanity checks
PR_STATE="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json state --jq '.state')"
PR_IS_DRAFT="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json isDraft --jq '.isDraft')"
PR_MERGABLE="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json mergeable --jq '.mergeable')"
PR_MERGESTATE="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json mergeStateStatus --jq '.mergeStateStatus')"

info "PR #$PR_NUMBER state=$PR_STATE draft=$PR_IS_DRAFT mergeable=$PR_MERGABLE mergeState=$PR_MERGESTATE"

if [ "$PR_STATE" != "OPEN" ]; then
  die "PR #$PR_NUMBER is not open (state=$PR_STATE). Aborting."
fi
if [ "$PR_IS_DRAFT" = "true" ]; then
  die "PR #$PR_NUMBER is a draft. Mark it ready for review before merging."
fi
if echo "$PR_MERGABLE" | grep -iq "CONFLICT"; then
  die "PR #$PR_NUMBER has conflicts. Resolve them before merging."
fi

# determine head SHA
HEAD_SHA="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json headRefOid --jq '.headRefOid')"
if [ -z "$HEAD_SHA" ] || [ "$HEAD_SHA" = "null" ]; then
  die "Unable to determine head commit for PR #$PR_NUMBER"
fi
info "Head commit: $HEAD_SHA"

# function to check combined state (statuses) and check-runs
check_ci_state() {
  local sha="$1"
  # Combined status ("success", "failure", "pending", "error")
  local combined
  combined="$(gh api -H "Accept: application/vnd.github+json" /repos/"$OWNER"/"$REPO_NAME"/commits/"$sha"/status --jq '.state' 2>/dev/null || echo "unknown")"

  # Check-runs summary
  local checks_json
  checks_json="$(gh api -H "Accept: application/vnd.github+json" /repos/"$OWNER"/"$REPO_NAME"/commits/"$sha"/check-runs 2>/dev/null || echo '{"check_runs":[]}')"
  local pending_count
  pending_count="$(echo "$checks_json" | jq '.check_runs | map(select(.status != "completed")) | length')"
  local failed_count
  failed_count="$(echo "$checks_json" | jq '[.check_runs[] | select(.conclusion=="failure" or .conclusion=="cancelled" or .conclusion=="timed_out" or .conclusion=="action_required")] | length')"

  # Decide:
  # - if failed_count > 0 -> return 2
  # - if combined == "failure" or "error" -> return 2
  # - if pending_count > 0 or combined == "pending" -> return 1
  # - else success -> return 0
  if [ "$failed_count" -gt 0 ]; then
    return 2
  fi
  if [ "$combined" = "failure" ] || [ "$combined" = "error" ]; then
    return 2
  fi
  if [ "$pending_count" -gt 0 ] || [ "$combined" = "pending" ]; then
    return 1
  fi
  return 0
}

# Optionally wait for checks
if [ "$WAIT_FOR_CHECKS" = "true" ]; then
  info "Polling CI for commit $HEAD_SHA (interval=${POLL_INTERVAL}s, max_attempts=${MAX_ATTEMPTS})..."
  attempt=0
  while [ "$attempt" -lt "$MAX_ATTEMPTS" ]; do
    attempt=$((attempt+1))
    if check_ci_state "$HEAD_SHA"; then
      info "CI checks passed or completed."
      break
    else
      status=$?
      if [ "$status" -eq 1 ]; then
        info "CI still running (attempt $attempt/$MAX_ATTEMPTS). Waiting ${POLL_INTERVAL}s..."
        sleep "$POLL_INTERVAL"
        continue
      elif [ "$status" -eq 2 ]; then
        die "CI checks reported failure. Aborting merge."
      else
        die "Unknown CI check result. Aborting."
      fi
    fi
  done

  if [ "$attempt" -ge "$MAX_ATTEMPTS" ]; then
    die "Timed out waiting for CI checks after $MAX_ATTEMPTS attempts."
  fi
fi

# confirmation
if [ "$AUTO_YES" != "true" ]; then
  read -rp "Proceed to merge PR #$PR_NUMBER ($PR_TITLE) into $BASE_BRANCH using '$MERGE_METHOD'? (y/N) " CONF
  if [ "${CONF,,}" != "y" ]; then
    die "User aborted merge."
  fi
fi

# perform merge using PR number (more robust than branch name)
info "Merging PR #$PR_NUMBER using method='$MERGE_METHOD'..."
if gh pr merge "$PR_NUMBER" --repo "$REPO" --"$MERGE_METHOD" --delete-branch; then
  info "PR #$PR_NUMBER merged and branch deletion requested (if permitted)."
  echo "PR URL: $PR_URL"
else
  die "gh pr merge failed; inspect PR: $PR_URL"
fi
