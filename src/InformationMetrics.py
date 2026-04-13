import math

def _round6(value):
	return round(value, 6)

def calculate_information_metrics(probabilities, coding_dict):
	"""
	Compute source coding metrics for a probability distribution and coding dictionary.

	Returns a dictionary with values rounded to 6 decimals.
	"""
	epsilon = 1e-12

	if not probabilities:
		raise ValueError("'probabilities' cannot be empty.")

	positive_symbols = [symbol for symbol, prob in probabilities.items() if prob > 0]
	if not positive_symbols:
		raise ValueError("'probabilities' must contain at least one positive probability.")

	missing_codes = [symbol for symbol in positive_symbols if symbol not in coding_dict]
	if missing_codes:
		raise ValueError(f"Missing codewords for symbols: {missing_codes}")

	avg_len_terms = []
	entropy_terms = []
	entropy_raw_terms = []
	avg_len_raw_terms = []

	for symbol in positive_symbols:
		p_i = probabilities[symbol]
		l_i = len(coding_dict[symbol])
		entropy_component = -(p_i * math.log2(p_i))
		avg_len_component = p_i * l_i
		entropy_raw_terms.append(entropy_component)
		avg_len_raw_terms.append(avg_len_component)

		entropy_terms.append(
			{
				"symbol": symbol,
				"formula": f"-({p_i:.6f} * log2({p_i:.6f}))",
				"value": _round6(entropy_component),
			}
		)
		avg_len_terms.append(
			{
				"symbol": symbol,
				"formula": f"{p_i:.6f} * {l_i}",
				"value": _round6(avg_len_component),
			}
		)

	# Entropy: H(S) = -sum(p_i * log2(p_i)) for p_i > 0
	entropy = sum(entropy_raw_terms)

	# Average code length: L_bar = sum(p_i * L_i)
	average_code_length = sum(avg_len_raw_terms)

	# Code efficiency: eta = H(S) / L_bar
	if average_code_length <= epsilon:
		efficiency = 0.0
	else:
		efficiency = entropy / average_code_length

	# Relative redundancy: R = 1 - eta
	redundancy = 1.0 - efficiency

	# Maximum entropy for equiprobable alphabet
	n = len(probabilities)
	max_entropy = math.log2(n) if n > 0 else 0.0

	# Fundamental theorem check: H(S) <= L_bar < H(S) + 1
	lower_ok = average_code_length + epsilon >= entropy
	upper_ok = average_code_length < (entropy + 1.0 + epsilon)
	theorem_holds = lower_ok and upper_ok

	if theorem_holds:
		theorem_message = (
			"Fundamental theorem verified: H(S) <= L_bar < H(S) + 1."
		)
	else:
		theorem_message = (
			"Fundamental theorem NOT verified: expected H(S) <= L_bar < H(S) + 1."
		)

	return {
		"entropy": _round6(entropy),
		"average_code_length": _round6(average_code_length),
		"efficiency": _round6(efficiency),
		"redundancy": _round6(redundancy),
		"max_entropy": _round6(max_entropy),
		"theorem_holds": theorem_holds,
		"theorem_message": theorem_message,
		"calculation_steps": {
			"entropy": {
				"expression": " + ".join(term["formula"] for term in entropy_terms),
				"result": f"{_round6(entropy):.6f}",
				"terms": entropy_terms,
			},
			"average_code_length": {
				"expression": " + ".join(term["formula"] for term in avg_len_terms),
				"result": f"{_round6(average_code_length):.6f}",
				"terms": avg_len_terms,
			},
			"efficiency": {
				"expression": f"{_round6(entropy):.6f} / {_round6(average_code_length):.6f}",
				"result": f"{_round6(efficiency):.6f}",
			},
			"redundancy": {
				"expression": f"1 - {_round6(efficiency):.6f}",
				"result": f"{_round6(redundancy):.6f}",
			},
			"max_entropy": {
				"expression": f"log2({n})",
				"result": f"{_round6(max_entropy):.6f}",
			},
			"theorem_verification": {
				"expression": f"{_round6(entropy):.6f} <= {_round6(average_code_length):.6f} < {_round6(entropy + 1.0):.6f}",
				"result": theorem_holds,
			},
		},
	}


def format_information_metrics_report(method_name, metrics):
	"""Return a clean formatted report for calculated coding metrics."""
	lines = [
		"#" * 60,
		f"INFORMATION METRICS: {method_name}",
		"#" * 60,
		f"Average Length L_bar:   {metrics['average_code_length']:.6f}",
		f"Efficiency eta:         {metrics['efficiency']:.6f}",
		f"Redundancy R:           {metrics['redundancy']:.6f}",
		f"Entropy H(S):           {metrics['entropy']:.6f}",
		f"Maximum Entropy H_max:  {metrics['max_entropy']:.6f}",
		f"Theorem Verification:   {metrics['theorem_message']}({metrics['theorem_holds']})",
		"-" * 60,
		"Intermediate Steps:",
		f"H(S):                   {metrics['calculation_steps']['entropy']['expression']} = {metrics['calculation_steps']['entropy']['result']}",
		f"H_Max:	              {metrics['calculation_steps']['max_entropy']['expression']} = {metrics['calculation_steps']['max_entropy']['result']}",
		f"L_bar:                  {metrics['calculation_steps']['average_code_length']['expression']} = {metrics['calculation_steps']['average_code_length']['result']}",
		f"eta:                    {metrics['calculation_steps']['efficiency']['expression']} = {metrics['calculation_steps']['efficiency']['result']}",
		f"R:                      {metrics['calculation_steps']['redundancy']['expression']} = {metrics['calculation_steps']['redundancy']['result']}",
		f"Theorem:                {metrics['calculation_steps']['theorem_verification']['expression']} -> {metrics['calculation_steps']['theorem_verification']['result']}",
	]
	return "\n".join(lines)