import json
import os
import time
import requests
from pathlib import Path

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")

SCHEMA_URL = f"{WEAVIATE_URL}/v1/schema"
OBJECTS_URL = f"{WEAVIATE_URL}/v1/objects"
META_URL = f"{WEAVIATE_URL}/v1/meta"

SCHEMA_DIR = Path("/app/db/schema")
SEED_DIR = Path("/app/db/seed")

RESET = os.getenv("RESET_SCHEMA", "false").lower() == "true"


def wait_for_weaviate(timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(META_URL, timeout=5)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Weaviate not ready in time")


def get_existing_classes():
    r = requests.get(SCHEMA_URL, timeout=10)
    r.raise_for_status()
    data = r.json()
    return {c["class"] for c in data.get("classes", [])}


def delete_class(class_name: str):
    r = requests.delete(f"{SCHEMA_URL}/{class_name}", timeout=30)
    # 200 or 204 is OK
    if r.status_code >= 400:
        raise RuntimeError(f"Failed to delete class {class_name}: {r.text}")


def create_class(schema: dict):
    r = requests.post(SCHEMA_URL, json=schema, timeout=30)
    # some endpoints may return empty body
    if r.status_code >= 400:
        raise RuntimeError(f"Failed to create class {schema.get('class')}: {r.text}")


def import_objects(class_name: str, objs: list[dict]):
    for obj in objs:
        payload = {"class": class_name, "properties": obj}
        r = requests.post(OBJECTS_URL, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"Failed to import object into {class_name}: {r.text}")


def main():
    print("Waiting for Weaviate...")
    wait_for_weaviate()
    print("Weaviate is up ✅")

    existing = get_existing_classes()

    # 1) Apply schemas (ordered by filename)
    schema_files = sorted(SCHEMA_DIR.glob("*.json"))
    if not schema_files:
        print("No schema files found.")
        return

    for f in schema_files:
        schema = json.loads(f.read_text(encoding="utf-8"))
        cname = schema["class"]

        if RESET and cname in existing:
            print(f"Reset enabled → deleting class: {cname}")
            delete_class(cname)
            existing.remove(cname)

        if cname not in existing:
            print(f"Creating class: {cname} (from {f.name})")
            create_class(schema)
        else:
            print(f"Class already exists: {cname} (skip)")

    # 2) Import seed data (file name prefix must match class or be configured)
    # Convention here: 01-faq-data.json -> class FAQ
    seed_files = sorted(SEED_DIR.glob("*.json"))
    for f in seed_files:
        name = f.name.lower()
        if "faq" in name:
            target_class = "FAQ"
        else:
            print(f"Skipping seed file (no rule): {f.name}")
            continue

        objs = json.loads(f.read_text(encoding="utf-8"))
        print(f"Importing {len(objs)} objects into {target_class} (from {f.name})")
        import_objects(target_class, objs)

    print("Bootstrap done ✅")


if __name__ == "__main__":
    main()
