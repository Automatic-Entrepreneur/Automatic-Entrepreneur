import typing
import numpy as np
from CompaniesHouse.CompanyInfo import CompanyInfo

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
	for attribute in attribute_map:
		extracted_data[attribute] = {}
	for year in range(start_year, end_year):
		try:
			account_info = company.getAccountInformation(year)
		except IndexError:
			continue
		except (
				NotImplementedError
		):  # Risky behaviour - how to indicate the graph isn't there
			continue
		for record in account_info:
			for attribute in extracted_data:
				if record["name"] == attribute:
					if record["startdate"] is None:
						record_year = int(record["instant"][0:4])
					else:
						record_year = int(record["startdate"][0:4])
					if record_year not in extracted_data[attribute]:
						extracted_data[attribute][record_year] = record["value"]
					else:
						extracted_data[attribute][record_year] = max(
							extracted_data[attribute][record_year], record["value"]
						)
	output = {}
	for attribute, data_by_year in extracted_data.items():
		output[attribute] = {"years": [], "values": []}
		for year, value in sorted(data_by_year.items(), key=lambda t: t[0]):
			output[attribute]["years"].append(year)
			output[attribute]["values"].append(value)
	return {"name": company.getName().title(), "data": output}
