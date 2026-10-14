#!/usr/bin/env python3
"""
List GitHub Actions workflows, runs, and releases; trigger workflows.

Features added:
- Save runs to JSON (pretty-printed) or CSV (--output)
- Client-side filtering with --since and --until (ISO dates)
- Trigger workflow_dispatch with --trigger-workflow (requires --ref)
- Output formats: json (default), csv, table
- Default owner/repo from env vars ACTIONS_OWNER / ACTIONS_REPO
- --list-releases to query releases (useful for actions/runner v2.303.0)

Usage examples:
  GITHUB_TOKEN=ghp_xxx python list_actions.py --list-workflows
  GITHUB_TOKEN=ghp_xxx python list_actions.py --list-runs --workflow-name deploy --since 2026-09-01 --until 2026-10-01 --format csv --output runs.csv
  GITHUB_TOKEN=ghp_xxx python list_actions.py --trigger-workflow --workflow-name deploy --ref main --inputs '{"env":"prod"}'
  GITHUB_TOKEN=ghp_xxx python list_actions.py --list-releases
"""
from __future__ import annotations
import os
import sys
import requests
import argparse
import json
import csv
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

API_BASE = "https://api.github.com"


def auth_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "termux-actions-list-script"
    }


def paginate(session: requests.Session, url: str, params: Optional[Dict[str, Any]] = None):
    params = params or {}
    while url:
        r = session.get(url, params=params)
        r.raise_for_status()
        yield r.json()
        link = r.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                next_url = part.split(";")[0].strip().strip("<>").strip()
                break
        url = next_url
        params = None


def list_workflows(owner: str, repo: str, token: str) -> List[Dict[str, Any]]:
    sess = requests.Session()
    sess.headers.update(auth_headers(token))
    url = f"{API_BASE}/repos/{owner}/{repo}/actions/workflows"
    r = sess.get(url)
    r.raise_for_status()
    data = r.json()
    return data.get("workflows", [])


def list_runs(owner: str, repo: str, token: str, workflow_id: Optional[int] = None,
              per_page: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sess = requests.Session()
    sess.headers.update(auth_headers(token))
    if workflow_id:
        url = f"{API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
    else:
        url = f"{API_BASE}/repos/{owner}/{repo}/actions/runs"
    params = {"per_page": per_page}
    if filters:
        params.update(filters)
    runs: List[Dict[str, Any]] = []
    for page in paginate(sess, url, params=params):
        items = page.get("workflow_runs") or page.get("runs") or []
        runs.extend(items)
    return runs


def list_releases(owner: str, repo: str, token: str, per_page: int = 100) -> List[Dict[str, Any]]:
    sess = requests.Session()
    sess.headers.update(auth_headers(token))
    url = f"{API_BASE}/repos/{owner}/{repo}/releases"
    releases: List[Dict[str, Any]] = []
    for page in paginate(sess, url, params={"per_page": per_page}):
        items = page if isinstance(page, list) else page.get("releases", page.get("items", []))
        releases.extend(items)
    return releases


def find_workflow_by_name(workflows: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    name_l = name.lower()
    for w in workflows:
        if (w.get("name") or "").lower() == name_l:
            return w
        path = (w.get("path") or "").lower()
        if path.endswith(name_l) or path.endswith(name_l + ".yml") or path.endswith(name_l + ".yaml"):
            return w
        if name_l in (w.get("name") or "").lower() or name_l in path:
            return w
    return None


def parse_iso(s: str) -> datetime:
    if s is None:
        raise ValueError("None passed to parse_iso")
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except Exception:
        fmts = ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S")
        for f in fmts:
            try:
                return datetime.strptime(s, f).replace(tzinfo=timezone.utc)
            except Exception:
                continue
    raise ValueError(f"Unrecognized date format: {s}")


def filter_runs_by_date(runs: List[Dict[str, Any]], since: Optional[str], until: Optional[str]) -> List[Dict[str, Any]]:
    if not since and not until:
        return runs
    since_dt = parse_iso(since) if since else None
    until_dt = parse_iso(until) if until else None
    out = []
    for r in runs:
        created = r.get("created_at")
        if not created:
            continue
        try:
            created_dt = parse_iso(created)
        except Exception:
            continue
        if since_dt and created_dt < since_dt:
            continue
        if until_dt and created_dt > until_dt:
            continue
        out.append(r)
    return out


def print_workflows(workflows: List[Dict[str, Any]]):
    for w in workflows:
        print(f"id={w.get('id')}\tname={w.get('name')}\tpath={w.get('path')}\tstate={w.get('state')}")


def print_runs_table(runs: List[Dict[str, Any]], limit: int = 50):
    headers = ["run_id", "workflow_id", "name", "status", "conclusion", "branch", "created_at"]
    rows = []
    for r in runs[:limit]:
        rows.append([
            str(r.get("id") or ""),
            str(r.get("workflow_id") or ""),
            r.get("name") or "",
            r.get("status") or "",
            r.get("conclusion") or "",
            r.get("head_branch") or "",
            r.get("created_at") or ""
        ])
    if rows:
        col_widths = [max(len(h), *(len(row[i]) for row in rows)) for i, h in enumerate(headers)]
    else:
        col_widths = [len(h) for h in headers]
    fmt = "  ".join("{:<" + str(w) + "}" for w in col_widths)
    print(fmt.format(*headers))
    print("-" * (sum(col_widths) + 2 * (len(col_widths) - 1)))
    for row in rows:
        print(fmt.format(*row))
    if len(runs) > limit:
        print(f"...stopped after {limit} runs (use --limit to change).")


def save_json(path: str, data: Any):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print(f"Wrote JSON to {path}")


def save_csv(path: str, runs: List[Dict[str, Any]]):
    fields = ["id", "workflow_id", "name", "status", "conclusion", "head_branch", "created_at", "html_url"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in runs:
            row = {k: r.get(k, "") for k in fields}
            row["id"] = r.get("id", "")
            w.writerow(row)
    print(f"Wrote CSV to {path}")


def trigger_workflow(owner: str, repo: str, token: str, workflow_id: Optional[int] = None,
                     workflow_name: Optional[str] = None, ref: str = "main", inputs: Optional[Dict[str, Any]] = None):
    sess = requests.Session()
    sess.headers.update(auth_headers(token))
    if workflow_name and not workflow_id:
        wf_list = list_workflows(owner, repo, token)
        found = find_workflow_by_name(wf_list, workflow_name)
        if not found:
            print(f"No workflow matching name '{workflow_name}' found.", file=sys.stderr)
            sys.exit(3)
        workflow_id = found.get("id")
    if not workflow_id:
        print("workflow id (or name) is required to trigger a workflow.", file=sys.stderr)
        sys.exit(2)
    url = f"{API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
    body = {"ref": ref}
    if inputs:
        body["inputs"] = inputs
    r = sess.post(url, json=body)
    if r.status_code in (204, 201):
        print(f"Workflow dispatch accepted (204). Workflow id={workflow_id} ref={ref}")
    else:
        print(f"Failed to dispatch workflow: {r.status_code} {r.text}", file=sys.stderr)
        r.raise_for_status()


def print_releases(releases: List[Dict[str, Any]]):
    for rel in releases:
        print(f"id={rel.get('id')}\ttag={rel.get('tag_name')}\tname={rel.get('name')}\tpublished_at={rel.get('published_at')}")


def main():
    p = argparse.ArgumentParser()
    default_owner = os.getenv("ACTIONS_OWNER") or os.getenv("ACTIONS_USER") or "termux"
    default_repo = os.getenv("ACTIONS_REPO") or os.getenv("ACTIONS_PROJECT") or "termux-app"

    p.add_argument("--owner", default=default_owner, help=f"repo owner (default from ACTIONS_OWNER or '{default_owner}')")
    p.add_argument("--repo", default=default_repo, help=f"repo name (default from ACTIONS_REPO or '{default_repo}')")

    p.add_argument("--list-workflows", action="store_true", help="list workflows")
    p.add_argument("--list-runs", action="store_true", help="list workflow runs")
    p.add_argument("--list-releases", action="store_true", help="list releases for repo")

    p.add_argument("--workflow-name", help="workflow name to filter (case-insensitive)")
    p.add_argument("--workflow-id", type=int, help="workflow id to list runs for or to trigger")
    p.add_argument("--branch", help="filter runs by branch")
    p.add_argument("--event", help="filter runs by event (push, workflow_dispatch, etc.)")
    p.add_argument("--status", help="filter runs by status (completed, in_progress, queued)")
    p.add_argument("--limit", type=int, default=50, help="max runs to print when using table output")

    p.add_argument("--since", help="ISO date (inclusive) to filter runs by created_at, e.g. 2026-09-01 or 2026-09-01T00:00:00Z")
    p.add_argument("--until", help="ISO date (inclusive) to filter runs by created_at")
    p.add_argument("--format", choices=["json", "csv", "table"], default="json", help="output format for runs (json,csv,table)")
    p.add_argument("--output", help="write output to file (JSON or CSV depending on --format)")

    p.add_argument("--trigger-workflow", action="store_true", help="trigger workflow_dispatch for a workflow (requires --ref)")
    p.add_argument("--ref", help="git ref (branch or tag) to use when triggering workflow (required for --trigger-workflow)")
    p.add_argument("--inputs", help="JSON string of inputs to workflow_dispatch (e.g. '{\"key\":\"value\"}')")

    args = p.parse_args()

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        print("Error: set GITHUB_TOKEN (or GH_TOKEN) environment variable with repo or workflow scopes.", file=sys.stderr)
        sys.exit(2)

    owner = args.owner
    repo = args.repo

    if args.list_workflows:
        wf = list_workflows(owner, repo, token)
        print_workflows(wf)
        return

    if args.list_releases:
        rels = list_releases(owner, repo, token)
        print_releases(rels)
        if args.output:
            save_json(args.output, rels)
        return

    if args.trigger_workflow:
        if not args.ref:
            print("--ref is required for --trigger-workflow", file=sys.stderr)
            sys.exit(2)
        inputs = None
        if args.inputs:
            try:
                inputs = json.loads(args.inputs)
            except Exception as e:
                print(f"Failed to parse --inputs JSON: {e}", file=sys.stderr)
                sys.exit(2)
        trigger_workflow(owner, repo, token, workflow_id=args.workflow_id, workflow_name=args.workflow_name, ref=args.ref, inputs=inputs)
        return

    if args.list_runs:
        workflow_id = args.workflow_id
        if args.workflow_name and not workflow_id:
            wf_list = list_workflows(owner, repo, token)
            found = find_workflow_by_name(wf_list, args.workflow_name)
            if not found:
                print(f"No workflow matching name '{args.workflow_name}' found.", file=sys.stderr)
                sys.exit(3)
            workflow_id = found.get("id")

        filters = {}
        if args.branch:
            filters["branch"] = args.branch
        if args.event:
            filters["event"] = args.event
        if args.status:
            filters["status"] = args.status

        runs = list_runs(owner, repo, token, workflow_id=workflow_id, filters=filters)
        runs = filter_runs_by_date(runs, args.since, args.until)

        if args.format == "table":
            print_runs_table(runs, limit=args.limit)
            if args.output:
                save_csv(args.output, runs)
            return

        if args.format == "json":
            if args.output:
                save_json(args.output, runs)
            else:
                print(json.dumps(runs, indent=2, ensure_ascii=False))
            return

        if args.format == "csv":
            if args.output:
                save_csv(args.output, runs)
            else:
                w = csv.writer(sys.stdout)
                fields = ["id", "workflow_id", "name", "status", "conclusion", "head_branch", "created_at", "html_url"]
                w.writerow(fields)
                for r in runs:
                    w.writerow([r.get(k, "") for k in fields])
            return

    p.print_help()


if __name__ == "__main__":
    main()
