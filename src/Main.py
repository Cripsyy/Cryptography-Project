from AlphabetAnalysis import analyze_pdfs
from Huffman import append_huffman_table, build_huffman_table
from ShannonFano import append_shannon_fano_table, build_shannon_fano_table
from InformationMetrics import calculate_information_metrics, format_information_metrics_report


def main():
	output_file = "Result.txt"
	total_probabilities = analyze_pdfs("../PDFS", output_file)

	shannon_table, shannon_levels = build_shannon_fano_table(total_probabilities)
	append_shannon_fano_table(output_file, shannon_table, shannon_levels)
	shannon_codes = {row["letter"]: row["coded_word"] for row in shannon_table}
	shannon_metrics = calculate_information_metrics(total_probabilities, shannon_codes)
	with open(output_file, "a", encoding="utf-8") as f:
		f.write("\n" + format_information_metrics_report("SHANNON-FANO", shannon_metrics) + "\n")

	huffman_table, huffman_levels = build_huffman_table(total_probabilities)
	append_huffman_table(output_file, huffman_table, huffman_levels)
	huffman_codes = {row["letter"]: row["coded_word"] for row in huffman_table}
	huffman_metrics = calculate_information_metrics(total_probabilities, huffman_codes)
	with open(output_file, "a", encoding="utf-8") as f:
		f.write("\n" + format_information_metrics_report("HUFFMAN", huffman_metrics) + "\n")


if __name__ == "__main__":
	main()