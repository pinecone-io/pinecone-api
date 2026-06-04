"""Unit tests for extract_spec_diff. Run: pytest .github/scripts/tests -v
(add .github/scripts to sys.path or run from there)."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from extract_spec_diff import diff_operations, diff_one_op, diff_schemas  # noqa: E402


def test_operation_added_and_removed():
    base = {"paths": {"/indexes": {"get": {"operationId": "list_indexes"},
                                    "post": {"operationId": "create_index"}}}}
    head = {"paths": {"/indexes": {"get": {"operationId": "list_indexes"}},
                      "/indexes/{name}": {"delete": {"operationId": "delete_index"}}}}
    by = {(c["id"], c["change"]): c for c in diff_operations(base, head)}
    assert by[("create_index", "removed")]["breaking"] is True
    assert by[("delete_index", "added")]["breaking"] is False


def test_parameter_breaking_rules():
    b = {"parameters": [{"name": "limit", "in": "query", "schema": {"type": "integer"}}]}
    h = {"parameters": [
        {"name": "limit", "in": "query", "schema": {"type": "string"}},
        {"name": "namespace", "in": "query", "required": True, "schema": {"type": "string"}},
    ]}
    details = {c["detail"]: c["breaking"] for c in diff_one_op("op", b, h)}
    assert details["parameter 'limit' type changed"] is True
    assert details["required parameter 'namespace' added"] is True


def test_optional_param_added_is_not_breaking():
    b = {"parameters": []}
    h = {"parameters": [{"name": "filter", "in": "query", "schema": {"type": "string"}}]}
    c = diff_one_op("op", b, h)[0]
    assert c["detail"] == "parameter 'filter' added"
    assert c["breaking"] is False


def test_param_format_change_is_breaking():
    b = {"parameters": [{"name": "id", "in": "query", "schema": {"type": "integer", "format": "int32"}}]}
    h = {"parameters": [{"name": "id", "in": "query", "schema": {"type": "integer", "format": "int64"}}]}
    details = {c["detail"]: c["breaking"] for c in diff_one_op("op", b, h)}
    assert details["parameter 'id' format changed"] is True
    assert "parameter 'id' type changed" not in details  # type unchanged, only format


def test_param_location_change_reported_once_as_breaking():
    b = {"parameters": [{"name": "name", "in": "query", "required": True, "schema": {"type": "string"}}]}
    h = {"parameters": [{"name": "name", "in": "path", "required": True, "schema": {"type": "string"}}]}
    out = diff_one_op("op", b, h)
    details = {c["detail"]: c["breaking"] for c in out}
    assert details["parameter 'name' moved from query to path"] is True
    # the relocation must NOT also surface as a remove + add
    assert not any("removed" in d or "added" in d for d in details)


def test_removed_response_code_is_breaking():
    b = {"responses": {"200": {}, "404": {}}}
    h = {"responses": {"200": {}}}
    details = {c["detail"]: c["breaking"] for c in diff_one_op("op", b, h)}
    assert details["response '404' removed"] is True


def test_added_response_code_is_not_flagged():
    b = {"responses": {"200": {}}}
    h = {"responses": {"200": {}, "429": {}}}
    assert all("response" not in c["detail"] for c in diff_one_op("op", b, h))


def test_schema_property_format_change_is_breaking():
    base = {"components": {"schemas": {"M": {"properties": {"ts": {"type": "string", "format": "date"}}}}}}
    head = {"components": {"schemas": {"M": {"properties": {"ts": {"type": "string", "format": "date-time"}}}}}}
    d = {c["detail"]: c["breaking"] for c in diff_schemas(base, head)}
    assert d["property 'ts' format changed"] is True


def test_schema_breaking_rules():
    base = {"components": {"schemas": {"Index": {
        "properties": {"name": {"type": "string"},
                       "metric": {"type": "string", "enum": ["cosine", "dotproduct"]}},
        "required": ["name"]}}}}
    head = {"components": {"schemas": {"Index": {
        "properties": {"metric": {"type": "integer", "enum": ["cosine"]},
                       "host": {"type": "string"}},
        "required": ["host"]}}}}
    d = {c["detail"]: c["breaking"] for c in diff_schemas(base, head)}
    assert d["property 'name' removed"] is True
    assert d["required property 'host' added"] is True
    assert d["property 'metric' type changed"] is True
    assert d["enum value 'dotproduct' removed from 'metric'"] is True


def test_cli_on_files(tmp_path):
    import json
    base = tmp_path / "base.yaml"
    head = tmp_path / "head.yaml"
    out = tmp_path / "diff.json"
    base.write_text("paths:\n  /x:\n    get:\n      operationId: getx\n")
    head.write_text("paths: {}\n")
    script = os.path.join(os.path.dirname(__file__), "..", "extract_spec_diff.py")
    r = subprocess.run([sys.executable, script, "--base", str(base), "--head", str(head),
                        "--service", "db_data", "--version", "2025-10", "--output", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    changes = json.loads(out.read_text())
    assert any(c["id"] == "getx" and c["change"] == "removed" and c["service"] == "db_data" for c in changes)
