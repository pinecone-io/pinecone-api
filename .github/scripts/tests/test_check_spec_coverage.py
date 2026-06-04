"""Unit test for check_spec_coverage. Run: pytest .github/scripts/tests -v"""
import json
import os
import subprocess
import sys


def test_maps_to_docs_and_sdks_and_unmapped(tmp_path):
    diff = [
        {"kind": "operation", "id": "create_index", "change": "modified", "breaking": True, "detail": "x"},
        {"kind": "schema", "id": "Index.host", "change": "added", "breaking": False, "detail": "y"},
        {"kind": "operation", "id": "unknown_op", "change": "added", "breaking": False, "detail": "z"},
    ]
    man = {"operations": {"create_index": {"docs": ["guides/index-data/create-an-index"], "sdks": ["python", "ts"]}},
           "schemas": {"Index": {"docs": ["guides/index-data/indexes"], "sdks": ["python"]}}}
    dp = tmp_path / "diff.json"
    mp = tmp_path / "man.json"
    op = tmp_path / "gaps.json"
    dp.write_text(json.dumps(diff))
    mp.write_text(json.dumps(man))
    script = os.path.join(os.path.dirname(__file__), "..", "check_spec_coverage.py")
    r = subprocess.run([sys.executable, script, "--spec-diff", str(dp),
                        "--manifest", str(mp), "--output", str(op)],
                       capture_output=True, text=True, cwd=str(tmp_path))
    assert r.returncode == 0, r.stderr
    gaps = json.loads(op.read_text())
    pages = {g["doc_page"] for g in gaps}
    assert "guides/index-data/create-an-index" in pages
    assert "guides/index-data/indexes" in pages  # schema property mapped via "Index"
    assert any(g["breaking"] for g in gaps)
    assert all(g["symbol"] != "unknown_op" for g in gaps)  # unmapped, not in gaps
