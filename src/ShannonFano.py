from AlphabetAnalysis import analyze_pdfs

def split_by_min_difference(items):
	"""Split a sorted list into two groups with the closest probability sums."""
	if len(items) <= 1:
		return items, []

	total = sum(prob for _, prob in items)
	best_idx = 1
	best_diff = float("inf")
	running = 0.0

	for i in range(1, len(items)):
		running += items[i - 1][1]
		left_sum = running
		right_sum = total - left_sum
		diff = abs(left_sum - right_sum)
		if diff < best_diff:
			best_diff = diff
			best_idx = i

	return items[:best_idx], items[best_idx:]


def build_shannon_fano_table(total_probabilities):
	"""
	Build Shannon-Fano coding table with columns:
	letter, probability, parent levels, coded word.
	"""
	symbols = [(ch, p) for ch, p in total_probabilities.items() if p > 0]
	symbols.sort(key=lambda x: x[1], reverse=True)

	if not symbols:
		return [], 0

	if len(symbols) == 1:
		letter, prob = symbols[0]
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
		for letter, prob in symbols
	}

	def recurse(group, prefix_list):
		if len(group) == 1:
			letter, _ = group[0]
			table[letter]["parent_levels"] = prefix_list
			table[letter]["coded_word"] = "".join(prefix_list)
			return

		left, right = split_by_min_difference(group)

		recurse(left, prefix_list + ["0"])
		recurse(right, prefix_list + ["1"])

	recurse(symbols, [])

	rows = [table[letter] for letter, _ in symbols]
	max_parent_levels = max(len(row["parent_levels"]) for row in rows)
	return rows, max_parent_levels


def format_shannon_fano_line(row, max_parent_levels):
	line = f"{row['letter']:<10} | {row['probability']:<12.6f}"
	for i in range(max_parent_levels):
		level_value = row["parent_levels"][i] if i < len(row["parent_levels"]) else ""
		line += f" | {level_value:<10}"
	line += f" | {row['coded_word']:<12}"
	return line


def append_shannon_fano_table(report_path, table, max_parent_levels):
	with open(report_path, "a", encoding="utf-8") as f:
		f.write("\n" + "#" * 60 + "\n")
		f.write("PART 3: SHANNON-FANO CODING TABLE\n")
		f.write("#" * 60 + "\n")

		header = f"{'Letter':<10} | {'Probability':<12}"
		for i in range(1, max_parent_levels + 1):
			header += f" | {f'Parent L{i}':<10}"
		header += f" | {'Coded Word':<12}"
		f.write(header + "\n")
		f.write("-" * len(header) + "\n")

		for row in table:
			f.write(format_shannon_fano_line(row, max_parent_levels) + "\n")


def main():
	total_probabilities = analyze_pdfs("../PDFS", "Result.txt")
	shannon_fano_table, max_parent_levels = build_shannon_fano_table(total_probabilities)
	append_shannon_fano_table("Result.txt", shannon_fano_table, max_parent_levels)


if __name__ == "__main__":
	main()
