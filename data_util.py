import typing
import numpy as np
from CompaniesHouse.CompanyInfo import CompanyInfo
from fuzzywuzzy import fuzz

trend_map = {1: "increased", -1: "decreased", 0: "remained steady"}

attribute_map = {
	"ProfitLoss": {1: "profit", -1: "loss", 0: "no profit or loss"},
	"FixedAssets": {
		1: "value",
		-1: "NEGATIVE value",
		0: "no change in value",
	},
	"CurrentAssets": {
		1: "value",
		-1: "NEGATIVE value",
		0: "no change in value",
	},
}


def compare(a: float, b: float) -> int:
	"""
	Compares two numbers and returns 1, -1, or 0
	:param a: number being focused on
	:param b: number being compared to a
	:return: 1 if a > b, -1 if a < b, 0 if a == b
	"""
	if a > b:
		return 1
	elif a < b:
		return -1
	else:
		return 0


def three_sigfig(n: float, comma=False) -> str:
	output = float(
		np.format_float_positional(
			n, precision=3, unique=False, fractional=False, trim="-"
		)
	)
	if comma:
		return f"{output:,}"
	else:
		return str(output)


def extract_data(
		company_id: str,
		start_year: int,
		end_year: int,
) -> dict[str, typing.Union[str, dict[str, dict[str, list[typing.Union[int, float]]]]]]:
	company = CompanyInfo(company_id)
	extracted_data = {}

	for year in range(start_year, end_year):
		try:
			account_info_for_this_year = company.get_account_information(year, pdf_accept=True)
			# print(f"grabbing info for {year}")
			# for record in account_info_for_this_year:
			# 	print(record)
		except IndexError:
			continue
		except (
				NotImplementedError
		):  # Risky behaviour - how to indicate the graph isn't there
			continue

		for attribute in attribute_map:
			for record in account_info_for_this_year: # find corresponding record
				if fuzz.partial_ratio(record["name"], attribute) > 60:  # arbitrary cutoff 60
					attribute_name = record["name"]
					if record["startdate"] is None:
						record_year = int(record["instant"][0:4])
					else:
						record_year = int(record["startdate"][0:4])

					if attribute_name not in extracted_data:
						extracted_data[attribute_name] = {}

					if record_year not in extracted_data[attribute_name]:
						extracted_data[attribute_name][record_year] = record["value"]
					else:
						extracted_data[attribute_name][record_year] = max(
							extracted_data[attribute_name][record_year], record["value"]
						)

	# choose which attributes to use
	attributes_to_use = dict.fromkeys(attribute_map.keys())
	for attribute in attribute_map:
		ratio = 0
		for contender in extracted_data:
			if contender == attribute: # prioritise exact match
				attributes_to_use[attribute] = attribute
				break
			this_ratio = fuzz.partial_ratio(contender, attribute)
			if this_ratio > ratio:  # 60 is arbitrary cutoff
				attributes_to_use[attribute] = contender

	# prepare output
	output = {}
	for attribute in attributes_to_use:
		if attributes_to_use[attribute] is not None:
			actual_attribute = attributes_to_use[attribute]
			if actual_attribute not in attribute_map:
				attribute_map[actual_attribute] = attribute_map["FixedAssets"]  # put value in attribute_map
			data_by_year = extracted_data[actual_attribute]
			output[actual_attribute] = {"years": [], "values": []}
			for year, value in sorted(data_by_year.items(), key=lambda t: t[0]):
				output[actual_attribute]["years"].append(year)
				output[actual_attribute]["values"].append(value)
		else:
			print(f"no data found for {attribute}")

	return {"name": company.get_name().title(), "data": output}


if __name__ == "__main__":
	extracted_data = extract_data('03824658', 2010, 2023)
	for entry in extracted_data["data"]:
		print(entry, ":", extracted_data["data"][entry])
	# print(original_extract_data('03824658', 2010, 2023))
