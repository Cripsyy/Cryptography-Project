"""
Standalone User Input Encoding/Decoding Module
Encodes and decodes user input using both Huffman and Shannon-Fano methods.
Uses pre-computed probabilities from PDF analysis.
"""

import os
from AlphabetAnalysis import analyze_pdfs
from Huffman import build_huffman_table
from ShannonFano import build_shannon_fano_table


def encode_text(text, codes_dict):
	"""Encode text using provided coding dictionary."""
	text_lower = text.lower()
	encoded_chars = []
	
	for char in text_lower:
		if char.isalpha() and char in codes_dict:
			encoded_chars.append((char, codes_dict[char]))
	
	return encoded_chars, "".join(code for char, code in encoded_chars)


def decode_text(encoded_string, codes_dict):
	"""Decode binary string using provided coding dictionary."""
	# Create reverse mapping
	reverse_dict = {code: char for char, code in codes_dict.items()}
	
	decoded_chars = []
	i = 0
	
	while i < len(encoded_string):
		found = False
		# Try to match codes of increasing length
		for length in range(1, len(encoded_string) - i + 1):
			code = encoded_string[i:i+length]
			if code in reverse_dict:
				decoded_chars.append(reverse_dict[code])
				i += length
				found = True
				break
		
		if not found:
			# No valid code found, skip one bit
			i += 1
	
	return "".join(decoded_chars)


def get_original_bit_size(text):
	total_bits = 0
	diacritics = "ăâîșțĂÂÎȘȚ"

	for char in text:
		if char in diacritics:
			total_bits += 16
		else:
			total_bits += 8
	return total_bits

def display_encoding_results(text, method_name, codes_dict, encoded_list, encoded_string, decoded_text):
	"""Display encoding results in formatted manner."""
	print(f"\n{'='*80}")
	print(f"         {method_name.upper()} ENCODING RESULTS")
	print(f"{'='*80}")

	original_alpha_text = "".join(c for c in text if c.isalpha())
	original_bit_size = get_original_bit_size(original_alpha_text)
	
	print(f"\n--- Individual Character Encodings ---")
	for char, code in encoded_list:
		print(f"  '{char}' → {code}")
	
	print(f"\n--- Complete Encoded Binary ---")
	print(f"  {encoded_string}")
	
	print(f"\n--- Statistics ---")
	print(f"  Original text length:  {len([c for c in text.lower() if c.isalpha()])} characters")
	print(f"  Original bit length:   {original_bit_size} bits")
	print(f"  Encoded binary length: {len(encoded_string)} bits")
	if len(encoded_string) > 0 and original_bit_size > 0:
		compression = (1 - len(encoded_string) / original_bit_size) * 100
		print(f"  Compression:           {compression:.2f}%")
	
	print(f"\n--- Decoded Text ---")
	print(f"  {decoded_text}")
	
	# Verify decoding
	original = "".join(c for c in text.lower() if c.isalpha())
	if decoded_text == original:
		print(f"  ✓ Decoding verified: matches original input")
	else:
		print(f"  ✗ Warning: decoded text differs from original")


def main():
	"""Main function for user input encoding/decoding."""
	print("\n" + "="*80)
	print("               TEXT ENCODING/DECODING WITH HUFFMAN & SHANNON-FANO")
	print("="*80)
	
	# Load pre-computed probabilities from PDF analysis
	print("\nLoading probabilities from PDF analysis...")
	temp_file = "temp_analysis.txt"
	try:
		probabilities = analyze_pdfs("../PDFS", temp_file)
	finally:
		if os.path.exists(temp_file):
			os.remove(temp_file)
	
	if not probabilities:
		print("Error: Could not load probabilities from PDFs.")
		return
	
	print(f"Loaded probabilities for {len(probabilities)} characters")
	
	# Get user input
	user_text = input("\nEnter text to encode: ").strip()
	
	if not user_text:
		print("Error: Empty input. Please enter some text.")
		return
	
	# Build Huffman coding table
	huffman_table, _ = build_huffman_table(probabilities)
	huffman_codes = {row["letter"]: row["coded_word"] for row in huffman_table}
	
	# Build Shannon-Fano coding table
	shannon_table, _ = build_shannon_fano_table(probabilities)
	shannon_codes = {row["letter"]: row["coded_word"] for row in shannon_table}
	
	# Encode using Huffman
	huffman_encoded_list, huffman_encoded_string = encode_text(user_text, huffman_codes)
	huffman_decoded = decode_text(huffman_encoded_string, huffman_codes)
	
	# Encode using Shannon-Fano
	shannon_encoded_list, shannon_encoded_string = encode_text(user_text, shannon_codes)
	shannon_decoded = decode_text(shannon_encoded_string, shannon_codes)
	
	# Display results
	display_encoding_results(
		user_text,
		"Huffman",
		huffman_codes,
		huffman_encoded_list,
		huffman_encoded_string,
		huffman_decoded
	)
	
	display_encoding_results(
		user_text,
		"Shannon-Fano",
		shannon_codes,
		shannon_encoded_list,
		shannon_encoded_string,
		shannon_decoded
	)
	
	print(f"\n{'='*80}\n")


if __name__ == "__main__":
	main()
