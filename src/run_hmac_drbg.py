import sys

from HMAC_DRBG import HMAC_DRBG
from AlphabetAnalysis import analyze_pdfs
from Huffman import build_huffman_table
from ShannonFano import build_shannon_fano_table
from InformationMetrics import calculate_information_metrics, format_information_metrics_report
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

    entropy_input = derive_entropy_bytes(probabilities)
    print()
    print(f"Derived entropy seed: {len(entropy_input)} bytes")
    print(f"  hex: {entropy_input.hex()[:48]}...")

    drbg = HMAC_DRBG(
        entropy_input=entropy_input,
        nonce=b"HMAC_DRBG_DEMO",
        personalization_string=b"Cryptography_Project",
    )

    print()
    print(f"Generating {num_bytes} random bytes using HMAC_DRBG...")
    print("-" * 50)

    random_bytes = drbg.generate(num_bytes)

    print(f"Random bytes ({len(random_bytes)} bytes):")
    print(f"  hex:  {random_bytes.hex()}")
    print(f"  raw:  {random_bytes}")

    integer_value = int.from_bytes(random_bytes, "big")
    print(f"  int:  {integer_value}")

    print()
    print("=" * 60)
    print()
    print("Usage:")
    print("  python run_hmac_drbg.py                  Use cached results")
    print("  python run_hmac_drbg.py --refresh        Re-run full analysis")
    print("  python run_hmac_drbg.py --bytes=64       Generate 64 random bytes")
    print()


if __name__ == "__main__":
    main()
