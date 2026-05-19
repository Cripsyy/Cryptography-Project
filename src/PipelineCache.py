import hashlib
import json
import os

CACHE_FILE = "pipeline_cache.json"


def save_pipeline_cache(probabilities, huffman_table, shannon_table, metrics):
    data = {
        "probabilities": probabilities,
        "huffman_table": huffman_table,
        "shannon_fano_table": shannon_table,
        "information_metrics": metrics,
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_pipeline_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def derive_entropy_bytes(probabilities, min_bytes=55):
    canonical = json.dumps(
        dict(sorted(probabilities.items())),
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    entropy = b""
    counter = 0
    while len(entropy) < min_bytes:
        entropy += hashlib.sha256(canonical + str(counter).encode()).digest()
        counter += 1

    return entropy[:min_bytes]
