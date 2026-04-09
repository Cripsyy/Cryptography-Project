import pdfplumber
import unicodedata
import os


def compute_normalized_metrics(counts_dict, total, precision=6):
    """Return per-letter percentage/probability so rounded sums are exactly 100 and 1."""
    metrics = {letter: {"percentage": 0.0, "probability": 0.0} for letter in counts_dict}

    if total <= 0:
        return metrics

    sorted_letters = sorted(counts_dict.items(), key=lambda x: x[1], reverse=True)
    top_letter = sorted_letters[0][0]

    for letter, count in counts_dict.items():
        probability = count / total
        percentage = probability * 100
        metrics[letter]["probability"] = round(probability, precision)
        metrics[letter]["percentage"] = round(percentage, precision)

    probability_sum = sum(v["probability"] for v in metrics.values())
    percentage_sum = sum(v["percentage"] for v in metrics.values())

    metrics[top_letter]["probability"] = round(
        metrics[top_letter]["probability"] + (1.0 - probability_sum),
        precision,
    )
    metrics[top_letter]["percentage"] = round(
        metrics[top_letter]["percentage"] + (100.0 - percentage_sum),
        precision,
    )

    return metrics

def analyze_pdfs(folder_path, output_txt):
    romanian_alphabet = "abcdefghijklmnopqrstuvwxyzăâîșț"
    file_data = {}

    total_map = {letter: 0 for letter in romanian_alphabet}
    total_letters = 0

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in that folder.")
        return {}

    for filename in pdf_files:
        file_path = os.path.join(folder_path, filename)
        file_data[filename] = {letter: 0 for letter in romanian_alphabet}
        file_count = 0

        print(f"Reading: {filename}...")

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    for char_obj in page.chars:
                        raw_char = char_obj['text'].lower()

                        normalized = unicodedata.normalize('NFC', raw_char)
                        mapping = {'ş': 'ș', 'ţ': 'ț'}
                        final_char = mapping.get(normalized, normalized)

                        if final_char in file_data[filename]:
                            file_data[filename][final_char] += 1
                            file_count += 1

                            total_map[final_char] += 1
                            total_letters += 1

            file_data[filename]['__total__'] = file_count

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            del file_data[filename]

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("PART 1: INDIVIDUAL FILE ANALYSIS\n")
        f.write("=" * 60 + "\n\n")

        for filename, counts in file_data.items():
            total = counts.pop('__total__')
            metrics = compute_normalized_metrics(counts, total)

            perc_sum = 0
            prob_sum = 0
            f.write(f"FILE: {filename}\n")
            f.write(f"Total Letters: {total}\n")
            f.write("-" * 45 + "\n")
            f.write(f"{'Letter':<10} | {'Count':<10} | {'Probability':<11} | {'Percentage':<10} \n")
            f.write("-" * 45 + "\n")

            sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            for char, count in sorted_items:
                perc = metrics[char]["percentage"]
                prob = metrics[char]["probability"]
                perc_sum += perc
                prob_sum += prob
                f.write(f"{char:<10} | {count:<10} | {prob:<11.6f} | {perc:<10.6f}%\n")
            f.write("\n" + "=" * 60 + "\n\n")

        f.write("\n" + "#" * 60 + "\n")
        f.write("PART 2: TOTAL (ALL FILES COMBINED)\n")
        f.write("#" * 60 + "\n")
        f.write(f"Total Files Analyzed: {len(file_data)}\n")
        f.write(f"Total Letters Found: {total_letters}\n")
        f.write("-" * 45 + "\n")
        f.write(f"{'Letter':<10} | {'Count':<10} | {'Probability':<11} | {'Percentage':<10} \n")
        f.write("-" * 45 + "\n")

        sorted_grand = sorted(total_map.items(), key=lambda x: x[1], reverse=True)
        total_metrics = compute_normalized_metrics(total_map, total_letters)
        total_probabilities = {char: data["probability"] for char, data in total_metrics.items()}
        perc_sum = 0
        prob_sum = 0
        for char, count in sorted_grand:
            perc = total_metrics[char]["percentage"]
            prob = total_metrics[char]["probability"]
            perc_sum += perc
            prob_sum += prob
            f.write(f"{char:<10} | {count:<10} | {prob:<11.6f} | {perc:<10.6f}%\n")

        perc_items = [f"{total_metrics[char]['percentage']:.6f}%" for char, _ in sorted_grand]
        prob_items = [f"{total_metrics[char]['probability']:.6f}" for char, _ in sorted_grand]
        f.write("The sum of percentages is: " + " + ".join(perc_items) + f" = {perc_sum:.6f}%\n")
        f.write("The sum of probabilities is: " + " + ".join(prob_items) + f" = {prob_sum:.6f}\n")

    print(f"\nFull report written to: {output_txt}")
    return total_probabilities

if __name__ == "__main__":
    analyze_pdfs("../PDFS", "Result.txt")
