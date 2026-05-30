#!/usr/bin/env python3
"""Digest cooldown gate.

Posts a `digest-cooldown` commit status on open PRs that bump an *external*
container image digest (same image:tag, digest changed). A PR comment stores
the date each digest was first observed; once every gated digest has aged
>= COOLDOWN_DAYS the status flips to success, letting Renovate merge
(requires platformAutomerge=false so Renovate honours non-required statuses).

Why this exists: Renovate's minimumReleaseAge cannot gate Docker digest
updates because the docker datasource has no releaseTimestamp for digests
(renovatebot/renovate#38656). timestamp-required leaves the PR stuck pending;
timestamp-optional merges immediately. This workflow supplies the cooldown.

Only pure digest bumps are gated:
  - version bumps (tag changed) -> Renovate's own minimumReleaseAge handles it
  - initial pins (no prior @sha256) -> not gated (image already in use)
  - skip-listed registries (first-party, signed) -> not gated
"""
import os
import re
import json
import subprocess
import datetime

REPO = os.environ["REPO"]
COOLDOWN_DAYS = int(os.environ.get("COOLDOWN_DAYS", "3"))
SKIP = [s.strip() for s in os.environ.get("SKIP_REGISTRIES", "").split(",") if s.strip()]
TODAY = os.environ.get("TODAY") or datetime.date.today().isoformat()
DRY_RUN = os.environ.get("DRY_RUN") == "1"

MARKER = "<!-- digest-cooldown -->"
STATE_RE = re.compile(r"<!-- digest-cooldown-state (\{.*?\}) -->")
CONTEXT = "digest-cooldown"
REF = re.compile(r"([A-Za-z0-9][A-Za-z0-9._/-]*(?::[A-Za-z0-9._-]+)?)@(sha256:[0-9a-f]{64})")


def gh(*args, stdin=None):
    return subprocess.run(["gh", *args], check=True, capture_output=True,
                          text=True, input=stdin).stdout


def is_skip(name):
    return any(name.startswith(p) for p in SKIP)


def parse_diff(diff):
    """Return {digest: image} for external pure-digest bumps."""
    old, new = {}, {}
    for line in diff.splitlines():
        if line[:3] in ("+++", "---"):
            continue
        if line.startswith("+"):
            for name, dig in REF.findall(line):
                new[name] = dig
        elif line.startswith("-"):
            for name, dig in REF.findall(line):
                old[name] = dig
    gated = {}
    for name, dig in new.items():
        if is_skip(name):
            continue
        if name in old and old[name] != dig:
            gated[dig] = name
    return gated


def age_days(iso):
    return (datetime.date.fromisoformat(TODAY) - datetime.date.fromisoformat(iso)).days


def render_comment(state, names):
    rows = []
    for dig, seen in sorted(state.items()):
        a = age_days(seen)
        status = "✅ ready" if a >= COOLDOWN_DAYS else f"⏳ {COOLDOWN_DAYS - a}d left"
        rows.append(f"| `{names.get(dig, '?')}` | `{dig[:19]}…` | {seen} | {status} |")
    return (
        f"{MARKER}\n"
        f"### 🕒 Image digest cooldown ({COOLDOWN_DAYS}d)\n\n"
        f"External image digest bumps wait {COOLDOWN_DAYS} days before this check passes.\n\n"
        f"| image | digest | first seen | status |\n"
        f"|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
        f"<!-- digest-cooldown-state {json.dumps(state, sort_keys=True)} -->"
    )


def find_comment(num):
    comments = json.loads(gh("api", f"repos/{REPO}/issues/{num}/comments", "--paginate"))
    for c in comments:
        if MARKER in c["body"]:
            m = STATE_RE.search(c["body"])
            return c["id"], (json.loads(m.group(1)) if m else {})
    return None, {}


def upsert_comment(num, cid, body):
    if DRY_RUN:
        print(f"[dry-run] {'PATCH' if cid else 'POST'} comment on #{num}:\n{body}\n")
        return
    if cid:
        gh("api", "--method", "PATCH", f"repos/{REPO}/issues/comments/{cid}", "-f", f"body={body}")
    else:
        gh("api", "--method", "POST", f"repos/{REPO}/issues/{num}/comments", "-f", f"body={body}")


def set_status(sha, state, desc):
    if DRY_RUN:
        print(f"[dry-run] status {state} on {sha[:12]}: {desc}")
        return
    gh("api", "--method", "POST", f"repos/{REPO}/statuses/{sha}",
       "-f", f"state={state}", "-f", f"context={CONTEXT}", "-f", f"description={desc[:140]}")


def main():
    prs = json.loads(gh("pr", "list", "--repo", REPO, "--state", "open",
                        "--limit", "100", "--json", "number,headRefOid"))
    for pr in prs:
        num, sha = pr["number"], pr["headRefOid"]
        gated = parse_diff(gh("pr", "diff", str(num), "--repo", REPO))
        if not gated:
            continue
        cid, state = find_comment(num)
        new_state = {dig: state.get(dig, TODAY) for dig in gated}
        if new_state != state or cid is None:
            upsert_comment(num, cid, render_comment(new_state, gated))
        pending = [COOLDOWN_DAYS - age_days(s) for s in new_state.values()
                   if age_days(s) < COOLDOWN_DAYS]
        if pending:
            set_status(sha, "pending",
                       f"{max(pending)}d left before {len(new_state)} external image "
                       f"digest(s) clear the {COOLDOWN_DAYS}d cooldown")
        else:
            set_status(sha, "success",
                       f"{len(new_state)} external image digest(s) aged >= {COOLDOWN_DAYS}d")
        print(f"PR #{num}: {len(new_state)} gated digest(s), "
              f"{'pending' if pending else 'success'}")


if __name__ == "__main__":
    main()
