#!/usr/bin/env python3
"""Map a spec-diff to affected docs.pinecone.io pages + impacted SDKs via the manifest.

Reads spec-diff.json (from extract_spec_diff.py) and spec-manifest.json, joins on
operation id / schema name, and writes spec-gaps.json. Changed surface absent from
the manifest is logged to spec-gaps-unmapped.json so the manifest can be kept current.
Sets the `has_gaps` GitHub Actions output.
"""
import argparse
import json
import os
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec-diff", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output", default="spec-gaps.json")
    a = ap.parse_args()

    diff = json.loads(Path(a.spec_diff).read_text())
    man = json.loads(Path(a.manifest).read_text())
    ops = man.get("operations", {})
    schs = man.get("schemas", {})

    gaps, unmapped = [], []
    for c in diff:
        if c["kind"] == "operation":
            entry = ops.get(c["id"])
        else:
            # schema ids may be "Schema" or "Schema.property" — map by schema name
            entry = schs.get(c["id"].split(".")[0])
        if not entry:
            unmapped.append(c)
            continue
        for page in entry.get("docs", []):
            gaps.append({
                "symbol": c["id"], "change": c["change"], "breaking": c.get("breaking", False),
                "doc_page": page, "sdks": entry.get("sdks", []), "detail": c.get("detail", ""),
            })

    Path(a.output).write_text(json.dumps(gaps, indent=2))
    if unmapped:
        Path("spec-gaps-unmapped.json").write_text(json.dumps(unmapped, indent=2))

    has_gaps = bool(gaps)
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as f:
            f.write(f"has_gaps={'true' if has_gaps else 'false'}\n")
    pages = len({g["doc_page"] for g in gaps})
    print(f"{len(gaps)} doc-gaps across {pages} page(s); {len(unmapped)} unmapped")


if __name__ == "__main__":
    main()
