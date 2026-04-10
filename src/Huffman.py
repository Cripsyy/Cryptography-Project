from heapq import heappop, heappush
from itertools import count

from AlphabetAnalysis import analyze_pdfs


def build_huffman_tree(total_probabilities):
	"""Build a Huffman tree from {symbol: probability} map."""
	symbols = [(ch, p) for ch, p in total_probabilities.items() if p > 0]

	if not symbols:
		return None, []

	symbols.sort(key=lambda x: x[1], reverse=True)

	if len(symbols) == 1:
		letter, prob = symbols[0]
		return (letter, prob), symbols

	order = count()
	heap = []

	for letter, prob in symbols:
		node = (letter, prob)
		heappush(heap, (prob, next(order), node))

	while len(heap) > 1:
		prob_left, _, left = heappop(heap)
		prob_right, _, right = heappop(heap)
		parent = (left, right)
		heappush(heap, (prob_left + prob_right, next(order), parent))

	root = heappop(heap)[2]
	return root, symbols


def build_huffman_table(total_probabilities):
	"""
	Build Huffman coding table with columns:
	letter, probability, parent levels, coded word.
	"""
	root, sorted_symbols = build_huffman_tree(total_probabilities)

	if root is None:
		return [], 0

	if len(sorted_symbols) == 1:
		letter, prob = sorted_symbols[0]
		return [
			{
				"letter": letter,
				"probability": prob,
				"coded_word": "0",
				"parent_levels": [],
			}
		], 0

	table = {
		letter: {"letter": letter, "probability": prob, "coded_word": "", "parent_levels": []}
		for letter, prob in sorted_symbols
	}

	def traverse(node, prefix_list):
		if isinstance(node[0], str):
			letter = node[0]
			table[letter]["parent_levels"] = prefix_list
			table[letter]["coded_word"] = "".join(prefix_list)
			return

		left, right = node
		traverse(left, prefix_list + ["0"])
		traverse(right, prefix_list + ["1"])

	traverse(root, [])

	rows = [table[letter] for letter, _ in sorted_symbols]
	max_parent_levels = max(len(row["parent_levels"]) for row in rows)
	return rows, max_parent_levels


def format_huffman_line(row, max_parent_levels):
	line = f"{row['letter']:<10} | {row['probability']:<12.6f}"
	for i in range(max_parent_levels):
		level_value = row["parent_levels"][i] if i < len(row["parent_levels"]) else ""
		line += f" | {level_value:<10}"
	line += f" | {row['coded_word']:<12}"
	return line


def append_huffman_table(report_path, table, max_parent_levels):
	with open(report_path, "a", encoding="utf-8") as f:
		f.write("\n" + "#" * 60 + "\n")
		f.write("PART 4: HUFFMAN CODING TABLE\n")
		f.write("#" * 60 + "\n")

		header = f"{'Letter':<10} | {'Probability':<12}"
		for i in range(1, max_parent_levels + 1):
			header += f" | {f'Parent L{i}':<10}"
		header += f" | {'Coded Word':<12}"
		f.write(header + "\n")
		f.write("-" * len(header) + "\n")

		for row in table:
			f.write(format_huffman_line(row, max_parent_levels) + "\n")


def main():
	total_probabilities = analyze_pdfs("../PDFS", "Result.txt")
	huffman_table, max_parent_levels = build_huffman_table(total_probabilities)
	append_huffman_table("Result.txt", huffman_table, max_parent_levels)


if __name__ == "__main__":
	main()
