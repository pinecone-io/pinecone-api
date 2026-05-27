#!/usr/bin/env python3
"""Diff two OpenAPI specs; classify each change as breaking or non-breaking.

Emits a JSON list of changes. Operations are keyed by operationId (falling back
to "<METHOD> <path>"); schemas by name (properties as "Schema.prop"). Used by the
spec-drift-detector workflow in both PR mode (git refs) and scheduled mode (files).

Zero runtime dependencies beyond pyyaml.
"""
import argparse
import json
import subprocess
from pathlib import Path

import yaml

METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def load(text: str) -> dict:
    return yaml.safe_load(text) or {}


def git_show(ref: str, path: str) -> str:
    """File contents at a git ref, or '' if absent on that side (new/deleted file)."""
    try:
        return subprocess.run(
            ["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True
        ).stdout
    except subprocess.CalledProcessError:
        return ""


def operations(spec: dict) -> dict:
    """{op_key: {method, path, op}} for every paths.<path>.<method>."""
    out = {}
    for path, methods in (spec.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        for m, op in methods.items():
            if m.lower() not in METHODS or not isinstance(op, dict):
                continue
            key = op.get("operationId") or f"{m.upper()} {path}"
            out[key] = {"method": m.upper(), "path": path, "op": op}
    return out


def params(op: dict) -> dict:
    out = {}
    for p in op.get("parameters") or []:
        if isinstance(p, dict) and "name" in p:
            out[(p["name"], p.get("in", ""))] = p
    return out


def schemas(spec: dict) -> dict:
    return ((spec.get("components") or {}).get("schemas")) or {}


def _type(d):
    if not isinstance(d, dict):
        return None
    s = d.get("schema", d)
    if not isinstance(s, dict):
        return None
    return s.get("type") or s.get("$ref")


def diff_operations(base: dict, head: dict) -> list[dict]:
    changes = []
    bo, ho = operations(base), operations(head)
    for k in bo.keys() - ho.keys():
        changes.append({"kind": "operation", "id": k, "change": "removed", "breaking": True,
                        "before": f"{bo[k]['method']} {bo[k]['path']}", "after": "",
                        "detail": "operation removed"})
    for k in ho.keys() - bo.keys():
        changes.append({"kind": "operation", "id": k, "change": "added", "breaking": False,
                        "before": "", "after": f"{ho[k]['method']} {ho[k]['path']}",
                        "detail": "operation added"})
    for k in bo.keys() & ho.keys():
        changes += diff_one_op(k, bo[k]["op"], ho[k]["op"])
    return changes


def diff_one_op(key: str, b: dict, h: dict) -> list[dict]:
    changes = []
    bp, hp = params(b), params(h)
    for name in bp.keys() - hp.keys():
        req = bool(bp[name].get("required"))
        changes.append({"kind": "operation", "id": key, "change": "modified", "breaking": req,
                        "before": f"param {name[0]}", "after": "",
                        "detail": f"{'required ' if req else ''}parameter '{name[0]}' removed"})
    for name in hp.keys() - bp.keys():
        req = bool(hp[name].get("required"))
        changes.append({"kind": "operation", "id": key, "change": "modified", "breaking": req,
                        "before": "", "after": f"param {name[0]}",
                        "detail": f"{'required ' if req else ''}parameter '{name[0]}' added"})
    for name in bp.keys() & hp.keys():
        pb, ph = bp[name], hp[name]
        if not pb.get("required") and ph.get("required"):
            changes.append({"kind": "operation", "id": key, "change": "modified", "breaking": True,
                            "before": f"{name[0]} optional", "after": f"{name[0]} required",
                            "detail": f"parameter '{name[0]}' now required"})
        if _type(pb) != _type(ph):
            changes.append({"kind": "operation", "id": key, "change": "modified", "breaking": True,
                            "before": str(_type(pb)), "after": str(_type(ph)),
                            "detail": f"parameter '{name[0]}' type changed"})
    return changes


def diff_schemas(base: dict, head: dict) -> list[dict]:
    changes = []
    bs, hs = schemas(base), schemas(head)
    for name in bs.keys() - hs.keys():
        changes.append({"kind": "schema", "id": name, "change": "removed", "breaking": True,
                        "before": name, "after": "", "detail": "schema removed"})
    for name in hs.keys() - bs.keys():
        changes.append({"kind": "schema", "id": name, "change": "added", "breaking": False,
                        "before": "", "after": name, "detail": "schema added"})
    for name in bs.keys() & hs.keys():
        changes += diff_one_schema(name, bs[name], hs[name])
    return changes


def diff_one_schema(name: str, b: dict, h: dict) -> list[dict]:
    changes = []
    bp = b.get("properties") or {}
    hp = h.get("properties") or {}
    breq, hreq = set(b.get("required") or []), set(h.get("required") or [])
    for prop in bp.keys() - hp.keys():
        changes.append({"kind": "schema", "id": f"{name}.{prop}", "change": "removed", "breaking": True,
                        "before": prop, "after": "", "detail": f"property '{prop}' removed"})
    for prop in hp.keys() - bp.keys():
        newreq = prop in hreq
        changes.append({"kind": "schema", "id": f"{name}.{prop}", "change": "added", "breaking": newreq,
                        "before": "", "after": prop,
                        "detail": f"{'required ' if newreq else ''}property '{prop}' added"})
    for prop in bp.keys() & hp.keys():
        if prop not in breq and prop in hreq:
            changes.append({"kind": "schema", "id": f"{name}.{prop}", "change": "modified", "breaking": True,
                            "before": "optional", "after": "required",
                            "detail": f"property '{prop}' now required"})
        if _type(bp[prop]) != _type(hp[prop]):
            changes.append({"kind": "schema", "id": f"{name}.{prop}", "change": "modified", "breaking": True,
                            "before": str(_type(bp[prop])), "after": str(_type(hp[prop])),
                            "detail": f"property '{prop}' type changed"})
        be = set(bp[prop].get("enum") or []) if isinstance(bp[prop], dict) else set()
        he = set(hp[prop].get("enum") or []) if isinstance(hp[prop], dict) else set()
        for removed in be - he:
            changes.append({"kind": "schema", "id": f"{name}.{prop}", "change": "modified", "breaking": True,
                            "before": str(removed), "after": "",
                            "detail": f"enum value '{removed}' removed from '{prop}'"})
    return changes


def diff(base: dict, head: dict) -> list[dict]:
    return diff_operations(base, head) + diff_schemas(base, head)


def main():
    ap = argparse.ArgumentParser(description="Diff two OpenAPI specs.")
    ap.add_argument("--base", help="Base spec file path")
    ap.add_argument("--head", help="Head spec file path")
    ap.add_argument("--base-ref", help="Base git ref (use with --path)")
    ap.add_argument("--head-ref", help="Head git ref (use with --path)")
    ap.add_argument("--path", help="Repo-relative spec path for git-ref mode")
    ap.add_argument("--service", default="")
    ap.add_argument("--version", default="")
    ap.add_argument("--output", default="spec-diff.json")
    a = ap.parse_args()

    if a.base_ref is not None and a.path:
        base = load(git_show(a.base_ref, a.path))
        head = load(git_show(a.head_ref, a.path))
    else:
        base = load(Path(a.base).read_text()) if a.base and Path(a.base).exists() else {}
        head = load(Path(a.head).read_text()) if a.head and Path(a.head).exists() else {}

    changes = diff(base, head)
    for c in changes:
        c["service"] = a.service
        c["version"] = a.version
    Path(a.output).write_text(json.dumps(changes, indent=2))
    nb = sum(1 for c in changes if c["breaking"])
    print(f"{len(changes)} changes ({nb} breaking) -> {a.output}")


if __name__ == "__main__":
    main()
