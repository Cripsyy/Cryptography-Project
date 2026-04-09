from AlphabetAnalysis import analyze_pdfs
from Huffman import append_huffman_table, build_huffman_table
from ShannonFano import append_shannon_fano_table, build_shannon_fano_table


def main():
	output_file = "Result.txt"
	total_probabilities = analyze_pdfs("../PDFS", output_file)

	shannon_table, shannon_levels = build_shannon_fano_table(total_probabilities)
	append_shannon_fano_table(output_file, shannon_table, shannon_levels)

	huffman_table, huffman_levels = build_huffman_table(total_probabilities)
	append_huffman_table(output_file, huffman_table, huffman_levels)


if __name__ == "__main__":
	main()