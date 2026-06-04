#!/usr/bin/env python3
"""
open_docs_stub_pr.py

Opens a draft PR in pinecone-io/docs with TODO annotations for each
doc page flagged by check_docs_coverage.py. Runs only on the scheduled
drift-detection job, not on every PR.

Requirements:
  - gh CLI (pre-installed on GitHub Actions ubuntu-latest runners)
  - DOCS_TOKEN env var: a PAT with `repo` scope on pinecone-io/docs

Usage:
    python .github/scripts/open_docs_stub_pr.py \
        --gaps docs-gaps.json \
        --docs-repo pinecone-io/docs \
        --token "$DOCS_TOKEN"
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path


def run(cmd: list[str], cwd: str | None = None, env: dict | None = None) -> None:
    print(f"  $ {' '.join(str(c) for c in cmd)}", flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gaps", default="docs-gaps.json")
    parser.add_argument("--docs-repo", default="pinecone-io/docs")
    parser.add_argument("--token", default=os.environ.get("DOCS_TOKEN", ""))
    args = parser.parse_args()

    if not args.token:
        print("Error: --token or DOCS_TOKEN required", file=sys.stderr)
        sys.exit(1)

    with open(args.gaps) as f:
        gaps = json.load(f)

    if not gaps:
        print("No gaps — nothing to open a PR for.")
        return

    today = date.today().isoformat()
    branch = f"chore/sdk-drift-{today}"
    pr_title = f"chore: update docs for SDK drift ({today})"

    # Group gaps by page so we insert one comment block per page
    pages: dict[str, list[dict]] = {}
    for gap in gaps:
        pages.setdefault(gap["doc_page"], []).append(gap)

    gh_env = {**os.environ, "GH_TOKEN": args.token}

    with tempfile.TemporaryDirectory() as tmpdir:
        run(["gh", "repo", "clone", args.docs_repo, tmpdir, "--", "--depth=1"], env=gh_env)
        run(["git", "checkout", "-b", branch], cwd=tmpdir)
        run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], cwd=tmpdir)
        run(["git", "config", "user.name", "github-actions[bot]"], cwd=tmpdir)

        modified = []
        for page_path, page_gaps in pages.items():
            # Docs repo stores guides as docs/guides/<page>.mdx
            mdx_path = Path(tmpdir) / f"{page_path}.mdx"
            if not mdx_path.exists():
                # Try without leading "guides/"
                alt = Path(tmpdir) / "docs" / f"{page_path}.mdx"
                if alt.exists():
                    mdx_path = alt
                else:
                    print(f"  Skipping {page_path} — .mdx not found in clone")
                    continue

            content = mdx_path.read_text()

            todos = []
            for g in page_gaps:
                msg = f"TODO(sdk-drift): `{g['symbol']}` {g['change']}"
                if g.get("before") and g.get("after"):
                    msg += f"\n  was: {g['before']}\n  now: {g['after']}"
                todos.append(f"{{/* {msg} */}}")

            stub_block = "\n".join(todos)

            # Insert after frontmatter (between second and third "---" markers)
            parts = content.split("---", 2)
            if len(parts) == 3:
                updated = f"---{parts[1]}---\n\n{stub_block}\n{parts[2]}"
            else:
                updated = f"{stub_block}\n\n{content}"

            mdx_path.write_text(updated)
            modified.append(str(mdx_path.relative_to(tmpdir)))
            print(f"  Annotated {page_path}")

        if not modified:
            print("No .mdx files found in clone for the flagged pages — no PR opened.")
            return

        run(["git", "add"] + modified, cwd=tmpdir)
        run(
            ["git", "commit", "-m", f"chore: add drift annotations ({today})"],
            cwd=tmpdir,
        )
        run(["git", "push", "origin", branch], cwd=tmpdir, env=gh_env)

        # Build PR body
        body = ["## SDK drift detected", ""]
        body.append(
            "The weekly `docs-drift-detector` found SDK method changes that may need doc updates."
        )
        body.append("")
        body.append("### Pages to review")
        body.append("")
        for page, page_gaps in pages.items():
            body.append(f"**`{page}`**")
            for g in page_gaps:
                item = f"- [ ] `{g['symbol']}` ({g['change']})"
                if g.get("before") and g.get("after"):
                    item += f": `{g['before']}` → `{g['after']}`"
                body.append(item)
            body.append("")
        body.append(
            "_Auto-generated stub. Mark items done as pages are updated. Close if not applicable._"
        )

        run(
            [
                "gh", "pr", "create",
                "--repo", args.docs_repo,
                "--head", branch,
                "--title", pr_title,
                "--body", "\n".join(body),
                "--draft",
            ],
            env=gh_env,
        )

    print(f"Draft PR opened: {pr_title}")


if __name__ == "__main__":
    main()
