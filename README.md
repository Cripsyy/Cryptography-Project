# Cryptography Project

**End-to-end cryptographic pipeline**: statistical text analysis, optimal prefix coding (Huffman & Shannon-Fano), information-theoretic metrics, and an HMAC-DRBG pseudorandom generator seeded from the derived entropy — all built from scratch in pure Python.

## Architecture

```
PDFS/                           .venv/
  *.pdf                           (dependencies)
    │
    ▼
AlphabetAnalysis.py ───► letter frequencies & probabilities
    │
    ├──► Huffman.py ────────────► Huffman coding table
    ├──► ShannonFano.py ────────► Shannon-Fano coding table
    └──► InformationMetrics.py ─► entropy, efficiency, redundancy
              │
              ▼
         Result.txt               pipeline_cache.json
              │                         │
              ▼                         ▼
     Main.py (orchestrator)    run_hmac_drbg.py (cached fast path)
              │                         │
              ▼                         ▼
   UserEncodingDecoding.py      HMAC_DRBG.py (NIST SP 800-90A)
   (interactive encode/decode)    │
                                  ▼
                           cryptographic random bytes
                           (with os.urandom(55) comparison)
```

## Modules

| File | Purpose |
|------|---------|
| `AlphabetAnalysis.py` | Parses Romanian PDFs with PyMuPDF. Counts occurrences of each letter (`a-z` + `ăâîșț`), normalizes probabilities so they sum to exactly 1. Returns `{letter: probability}`. |
| `Huffman.py` | Builds a Huffman encoding tree from the probability distribution. Produces a table of letters, probabilities, parent-level bits, and final codewords. |
| `ShannonFano.py` | Builds a Shannon-Fano encoding tree via recursive min-difference splitting. Produces the same table format as Huffman. |
| `InformationMetrics.py` | Computes entropy `H(S)`, average code length `L̃`, efficiency `η`, and redundancy `R`. Verifies the fundamental coding theorem `H(S) ≤ L̃ < H(S)+1`. |
| `Main.py` | Orchestrator. Runs the full pipeline (analyze → Huffman → Shannon-Fano → metrics) and writes `Result.txt`. |
| `UserEncodingDecoding.py` | Interactive CLI. Takes user text input and encodes/decodes it with both Huffman and Shannon-Fano codes. Shows compression rates and verifies round-trip correctness. |
| `HMAC_DRBG.py` | Pure-stdlib implementation of NIST SP 800-90A Section 10.1.2 (HMAC-DRBG with SHA-256). Includes `derive_entropy_input()` for building a 55-byte seed from probability data. |
| `PipelineCache.py` | Saves/loads pipeline results to `pipeline_cache.json`. Avoids re-analyzing PDFs on every run. Also provides `derive_entropy_bytes()` for deterministic entropy derivation. |
| `run_hmac_drbg.py` | Demo script. Seeds two HMAC-DRBG instances — one from project-derived entropy (deterministic), one from `os.urandom(55)` (non-deterministic) — and displays them side by side. |

## HMAC-DRBG (NIST SP 800-90A) implementation details

| Parameter | Value (SHA-256) |
|-----------|-----------------|
| `outlen` | 32 bytes |
| `seedlen` | 55 bytes |
| `max_bytes_per_request` | 65,536 |
| `reseed_interval` | 2⁴⁸ |

The class mirrors the NIST specification exactly:

- **Instantiation** — `K = 0x00…`, `V = 0x01…`, then 4 HMAC rounds mix in the seed material
- **`_update(data)`** — `K = HMAC(K, V ‖ 0x00 ‖ data)`, `V = HMAC(K, V)`, plus a second round with `0x01` if data is non-empty
- **`generate(n)`** — loops `V = HMAC(K, V)`, concatenates, truncates, then calls `_update` for backtracking resistance
- **`reseed(entropy)`** — re-mixes fresh entropy into the state, resets the reseed counter

## Dependencies

```
pip install PyMuPDF
```

All other modules use only the Python standard library (`hashlib`, `hmac`, `json`, `os`, `sys`, `itertools`, `math`, `heapq`, `unicodedata`).

## Quick start

```bash
# Activate the virtual environment
.venv\Scripts\activate

# 1. Full analysis pipeline (writes Result.txt + pipeline_cache.json)
python src\Main.py

# 2. Interactive encode/decode with your own text
python src\UserEncodingDecoding.py

# 3. HMAC-DRBG — compare project-derived entropy vs os.urandom(55)
python src\run_hmac_drbg.py                # uses cached results
python src\run_hmac_drbg.py --refresh      # re-runs full pipeline
python src\run_hmac_drbg.py --bytes=64     # generate 64 random bytes
```

## File structure

```
.
├── PDFS/                          # Romanian-language PDF corpus
├── src/
│   ├── AlphabetAnalysis.py        # PDF letter-frequency analysis
│   ├── Huffman.py                 # Huffman coding
│   ├── ShannonFano.py             # Shannon-Fano coding
│   ├── InformationMetrics.py      # Entropy / efficiency / redundancy
│   ├── Main.py                    # Full pipeline orchestrator
│   ├── UserEncodingDecoding.py    # Interactive encoder/decoder
│   ├── HMAC_DRBG.py               # NIST SP 800-90A HMAC-DRBG
│   ├── PipelineCache.py           # Pipeline caching layer
│   ├── run_hmac_drbg.py           # DRBG comparison demo
│   ├── Result.txt                 # Generated analysis report
│   └── pipeline_cache.json        # Cached pipeline state
├── .venv/                         # Virtual environment
├── .gitignore
└── README.md
```
