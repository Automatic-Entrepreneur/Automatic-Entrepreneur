from CompaniesHouse.CompanyInfo import CompanyInfo


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


def extract_data(
		company_id: str,
		attribute_map: dict[str, dict[int, str]],
		start_year: int,
		end_year: int
) -> dict[str, list[tuple[float, int]]]:
	company = CompanyInfo(company_id)

	extracted_data = {}
	for attribute in attribute_map:
		extracted_data[attribute] = {}

	for year in range(start_year, end_year):
		account_info = company.getAccountInformation(year)
		for record in account_info:
			for attribute in extracted_data:
				if record['name'] == attribute:
					if record["startdate"] is None:
						time = int(record["instant"][0:4])
					else:
						time = int(record["startdate"][0:4])
					if time not in extracted_data[attribute]:
						extracted_data[attribute][time] = record["value"]
					else:
						extracted_data[attribute][time] = max(extracted_data[attribute][time], record["value"])

	for attribute, data_by_year in extracted_data.items():
		extracted_data[attribute] = sorted([(value, year) for year, value in data_by_year.items()], key=lambda t: t[1])
	return extracted_data


def data_summary(values_by_year: list[tuple[float, int]]) -> list[dict[str, int | list[list[int]]]]:
	prev = values_by_year[0]
	trend_list = [{
		"sign": compare(prev[0], 0),
		"trend": [[0, prev[1], prev[1]]]
	}]

	for profitloss, year in values_by_year[1:]:
		sign = compare(profitloss, 0)
		direction = compare(profitloss, prev[0])
		if trend_list[-1]["sign"] == sign or sign == 0:
			trends = trend_list[-1]["trend"]
			if trends[-1][0] == direction:
				trends[-1][2] = year
			else:
				trends.append([direction, prev[1], year])
		else:
			trend_list.append({
				"sign": sign,
				"trend": [[direction, prev[1], year]]
			})

		prev = (profitloss, year)

	return trend_list


def format_summary(values_by_year: list[dict[str, int | list[list[int]]]], data_words: dict[int, str]) -> str:
	trend_words = {1: "increasing", -1: "decreasing", 0: "steady"}
	output = []
	for section in values_by_year:
		for trend in section["trend"]:
			if trend[1] != trend[2]:
				s = section["sign"]
				if s != 0:
					keywords = f"{trend_words[s * trend[0]]} {data_words[s]}"
				else:
					keywords = data_words[s]
				output.append(
					f"There was {keywords} from {trend[1]} to {trend[2]}."
				)
	return "\n".join(output)


def generate_single_summary(
		extracted_data: list[dict[str, int | list[list[int]]]],
		attribute_map: dict[str, dict[int, str]],
		attribute: str
) -> str:
	if attribute not in attribute_map:
		raise NotImplementedError(f"{attribute} summary not implemented")
	else:
		return format_summary(extracted_data, attribute_map[attribute])


def overall_summary(company_id: str, start_year: int, end_year: int) -> list[str]:
	attribute_map = {
		"ProfitLoss": {
			1: "profit",
			-1: "loss",
			0: "no profit or loss"
		},
		"FixedAssets": {
			1: "value of fixed assets",
			-1: "NEGATIVE value of fixed assets",
			0: "no change in the value of fixed assets"
		},
		"CurrentAssets": {
			1: "value of current assets"
		}
	}

	data = extract_data(company_id, attribute_map, start_year, end_year)
	print(data)
	print()

	return [
		generate_single_summary(data_summary(values), attribute_map, data_attribute)
		for data_attribute, values in data.items()
	]


if __name__ == "__main__":
	for summary in overall_summary("03824658", 2018, 2023):
		print(summary)
		print()
