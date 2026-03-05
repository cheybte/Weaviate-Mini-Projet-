import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8082")
GRAPHQL_ENDPOINT = f"{WEAVIATE_URL}/v1/graphql"
SCHEMA_ENDPOINT = f"{WEAVIATE_URL}/v1/schema"


def graphql(query: str) -> dict:
    r = requests.post(
        GRAPHQL_ENDPOINT,
        json={"query": query},
        headers={"Content-Type": "application/json"},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def wv_get(url: str) -> dict:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def wv_post(url: str, payload: dict) -> dict:
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    return r.json() if r.text.strip() else {"ok": True}


def wv_delete(url: str) -> dict:
    r = requests.delete(url, timeout=20)
    r.raise_for_status()
    return {"ok": True}


def unwrap_type(t: dict) -> str | None:
    cur = t
    while cur:
        if cur.get("name"):
            return cur["name"]
        cur = cur.get("ofType")
    return None


@app.get("/health")
def health():
    return jsonify({"ok": True, "weaviate": WEAVIATE_URL})


# --------------------------
# 1) LIST TABLES (GraphQL introspection)
# --------------------------
@app.get("/tables")
def tables():
    q1 = """
    {
      __schema {
        queryType {
          fields {
            name
            type { name kind ofType { name kind ofType { name kind ofType { name kind }}}}
          }
        }
      }
    }
    """
    data1 = graphql(q1)

    if "errors" in data1 and data1["errors"]:
        return jsonify({
            "ok": False,
            "error": "GraphQL introspection not available.",
            "details": data1["errors"],
            "hint": "You can list schema via REST: GET /v1/schema"
        }), 500

    fields = data1["data"]["__schema"]["queryType"]["fields"]
    get_field = next((f for f in fields if f["name"] == "Get"), None)
    if not get_field:
        return jsonify({"ok": False, "error": "Cannot find root field 'Get'."}), 500

    get_type_name = unwrap_type(get_field["type"])
    if not get_type_name:
        return jsonify({"ok": False, "error": "Cannot resolve type name for 'Get'."}), 500

    q2 = f"""
    {{
      __type(name: "{get_type_name}") {{
        fields {{ name }}
      }}
    }}
    """
    data2 = graphql(q2)

    if "errors" in data2 and data2["errors"]:
        return jsonify({"ok": False, "error": "Failed to read Get fields.", "details": data2["errors"]}), 500

    class_names = sorted({f["name"] for f in (data2["data"]["__type"]["fields"] or [])})
    return jsonify({"ok": True, "tables": class_names, "source": "graphql_introspection"})


# --------------------------
# 2) CREATE TABLE (Collection/Class) - REST schema
# --------------------------
@app.post("/tables")
def create_table():
    """
    Body example:
    {
      "name": "FAQ",
      "properties": [
        {"name":"question","dataType":["text"]},
        {"name":"answer","dataType":["text"]},
        {"name":"tag","dataType":["text"]}
      ],
      "vectorizer": "text2vec-transformers"
    }
    """
    body = request.get_json(force=True, silent=False)

    name = body.get("name")
    if not name:
        return jsonify({"ok": False, "error": "Missing field: name"}), 400

    vectorizer = body.get("vectorizer", "text2vec-transformers")
    properties = body.get("properties", [])

    payload = {
        "class": name,
        "vectorizer": vectorizer,
        "properties": properties,
    }

    try:
        wv_post(SCHEMA_ENDPOINT, payload)
        return jsonify({"ok": True, "created": name})
    except requests.HTTPError as e:
        return jsonify({"ok": False, "error": "Failed to create table", "details": e.response.text}), 500


# --------------------------
# 3) LIST COLUMNS of a TABLE - REST schema
# --------------------------
@app.get("/tables/<table>/columns")
def list_columns(table: str):
    try:
        schema = wv_get(f"{SCHEMA_ENDPOINT}/{table}")
        # schema contains "class", "properties", etc.
        props = schema.get("properties", [])
        columns = [{"name": p.get("name"), "dataType": p.get("dataType")} for p in props]
        return jsonify({"ok": True, "table": table, "columns": columns})
    except requests.HTTPError as e:
        return jsonify({"ok": False, "error": "Failed to read table schema", "details": e.response.text}), 500


# --------------------------
# 4) ADD COLUMN (Property) - REST schema
# --------------------------
@app.post("/tables/<table>/columns")
def add_column(table: str):
    """
    Body example:
    { "name": "source", "dataType": ["text"] }
    """
    body = request.get_json(force=True, silent=False)
    if not body.get("name") or not body.get("dataType"):
        return jsonify({"ok": False, "error": "Body must include: name, dataType"}), 400

    try:
        wv_post(f"{SCHEMA_ENDPOINT}/{table}/properties", body)
        return jsonify({"ok": True, "table": table, "added": body.get("name")})
    except requests.HTTPError as e:
        return jsonify({"ok": False, "error": "Failed to add column", "details": e.response.text}), 500


# --------------------------
# 5) DELETE TABLE (Class) - REST schema
# --------------------------
@app.delete("/tables/<table>")
def delete_table(table: str):
    try:
        wv_delete(f"{SCHEMA_ENDPOINT}/{table}")
        return jsonify({"ok": True, "deleted": table})
    except requests.HTTPError as e:
        return jsonify({"ok": False, "error": "Failed to delete table", "details": e.response.text}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)