import os
import sys

from HMAC_DRBG import HMAC_DRBG
from AlphabetAnalysis import analyze_pdfs
from Huffman import build_huffman_table
from ShannonFano import build_shannon_fano_table
from InformationMetrics import calculate_information_metrics
from PipelineCache import save_pipeline_cache, load_pipeline_cache, derive_entropy_bytes


def run_full_pipeline():
    print("Running full analysis pipeline (this may take a moment)...")
    print("-" * 50)

    output_file = "Result.txt"
    probabilities = analyze_pdfs("../PDFS", output_file)
    print(f"  PDF analysis complete: {len(probabilities)} letters")

    huffman_table, _ = build_huffman_table(probabilities)
    print("  Huffman table built")

    shannon_table, _ = build_shannon_fano_table(probabilities)
    print("  Shannon-Fano table built")

    huffman_codes = {row["letter"]: row["coded_word"] for row in huffman_table}
    shannon_codes = {row["letter"]: row["coded_word"] for row in shannon_table}

    huffman_metrics = calculate_information_metrics(probabilities, huffman_codes)
    shannon_metrics = calculate_information_metrics(probabilities, shannon_codes)

    metrics = {
        "huffman": huffman_metrics,
        "shannon_fano": shannon_metrics,
    }

    save_pipeline_cache(probabilities, huffman_table, shannon_table, metrics)
    print("  Pipeline cached to pipeline_cache.json")

    return probabilities, metrics


def load_or_run_pipeline(force_refresh=False):
    if not force_refresh:
        cached = load_pipeline_cache()
        if cached is not None:
            print("Loaded cached pipeline results (pipeline_cache.json)")
            print("-" * 50)
            return cached["probabilities"], cached["information_metrics"]

    return run_full_pipeline()


def print_metric(metrics, key):
    m = metrics[key]
    print(f"  Entropy H(S):        {m['entropy']:.6f}")
    print(f"  Avg code length:     {m['average_code_length']:.6f}")
    print(f"  Efficiency:          {m['efficiency']:.6f}")
    print(f"  Redundancy:          {m['redundancy']:.6f}")


def main():
    print("=" * 60)
    print("HMAC-DRBG — Entropy-Seeded Cryptographic Random Generator")
    print("=" * 60)
    print()

    force_refresh = "--refresh" in sys.argv
    num_bytes = 32

    for i, arg in enumerate(sys.argv):
        if arg.startswith("--bytes="):
            try:
                num_bytes = int(arg.split("=")[1])
            except ValueError:
                print(f"Invalid --bytes value, using default {num_bytes}")
        elif arg == "--bytes" and i + 1 < len(sys.argv):
            try:
                num_bytes = int(sys.argv[i + 1])
            except ValueError:
                print(f"Invalid --bytes value, using default {num_bytes}")

    probabilities, metrics = load_or_run_pipeline(force_refresh)

    print()
    print("Entropy source metrics (from analyzed text):")
    print_metric(metrics, "huffman")
    print()
    print_metric(metrics, "shannon_fano")

    entropy_text = derive_entropy_bytes(probabilities)
    entropy_urandom = os.urandom(55)

    print()
    print("=" * 70)
    print("  PARALLEL COMPARISON: Project-derived entropy vs os.urandom(55)")
    print("=" * 70)
    print()

    def format_seed(label, seed_bytes):
        print(f"  {label} seed ({len(seed_bytes)} bytes):")
        print(f"    hex: {seed_bytes.hex()}")
        print()

    format_seed("Project-derived", entropy_text)
    format_seed("os.urandom(55) ", entropy_urandom)

    common_nonce = b"HMAC_DRBG_DEMO"
    common_pers = b"Cryptography_Project"

    drbg_text = HMAC_DRBG(
        entropy_input=entropy_text,
        nonce=common_nonce,
        personalization_string=common_pers,
    )
    drbg_rand = HMAC_DRBG(
        entropy_input=entropy_urandom,
        nonce=common_nonce,
        personalization_string=common_pers,
    )

    out_text = drbg_text.generate(num_bytes)
    out_rand = drbg_rand.generate(num_bytes)

    print("-" * 70)
    print(f"  Generated output ({num_bytes} bytes each)")
    print("-" * 70)
    print()
    print(f"  {'Source':<30} {'Hex output'}")
    print(f"  {'-'*30} {'-'*40}")
    print(f"  {'Project-derived':<30} {out_text.hex()}")
    print(f"  {'os.urandom(55)':<30} {out_rand.hex()}")
    print()

    int_text = int.from_bytes(out_text, "big")
    int_rand = int.from_bytes(out_rand, "big")
    print(f"  {'Source':<30} {'Integer value'}")
    print(f"  {'-'*30} {'-'*40}")
    print(f"  {'Project-derived':<30} {int_text}")
    print(f"  {'os.urandom(55)':<30} {int_rand}")
    print()

    print("-" * 70)
    print("  Comparison summary")
    print("-" * 70)
    print()

    same_text_repeat = drbg_text.generate(num_bytes) if num_bytes <= 32 else b""
    same_rand_repeat = drbg_rand.generate(num_bytes) if num_bytes <= 32 else b""

    print(f"  Project-derived entropy:")
    print(f"    Deterministic: yes (same PDFs -> same output every run)")
    print(f"    Next generate differs from first: {out_text != same_text_repeat}")
    print()
    print(f"  os.urandom(55) entropy:")
    print(f"    Deterministic: no (different every run)")
    print(f"    Next generate differs from first: {out_rand != same_rand_repeat}")
    print()
    print(f"  Two sources produce different output: {out_text != out_rand}")
    print()

if __name__ == "__main__":
    main()
