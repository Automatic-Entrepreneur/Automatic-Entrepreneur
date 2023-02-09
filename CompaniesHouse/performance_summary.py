from data_extraction import trend_map, attribute_map, extract_data


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


def data_summary(
		records: dict[str, list[int | float]]
) -> list[dict[str, int | list[dict[str, int | float]]]]:
	values_by_year = list(zip(records["values"], records["years"]))
	prev = values_by_year[0]
	trends_list = [
		{
			"sign": compare(prev[0], 0),
			"trends": [
				{
					"trend": 0,
					"startVal": prev[0],
					"endVal": prev[0],
					"startYear": prev[1],
					"endYear": prev[1],
				}
			],
		}
	]

	for value, year in values_by_year[1:]:
		sign = compare(value, 0)
		trend = compare(value, prev[0])
		if trends_list[-1]["sign"] == sign or sign == 0:
			trends = trends_list[-1]["trends"]
			if trends[-1]["trend"] == trend:
				trends[-1]["endVal"] = value
				trends[-1]["endYear"] = year
			else:
				trends.append(
					{
						"trend": trend,
						"startVal": prev[0],
						"endVal": value,
						"startYear": prev[1],
						"endYear": year,
					}
				)
		else:
			trends_list.append(
				{
					"sign": sign,
					"trends": [
						{
							"trend": trend,
							"startVal": prev[0],
							"endVal": value,
							"startYear": prev[1],
							"endYear": year,
						}
					],
				}
			)
		prev = (value, year)
	return trends_list


def format_summary(
		values_by_year: list[dict[str, int | list[dict[str, int | float]]]],
		sign_map: dict[int, str],
) -> list[str]:
	output = []
	for section in values_by_year:
		for trend in section["trends"]:
			if trend["startYear"] != trend["endYear"]:
				s = section["sign"]
				t = s * trend["trend"]
				keywords1 = (
					f"{sign_map[s]}" if s == 0 else f"{sign_map[s]} {trend_map[t]}"
				)
				keywords2 = (
					f"at {trend['startVal']} GBP."
					if t == 0
					else f"from {trend['startVal']} to {trend['endVal']} GBP."
				)
				output.append(
					f"{trend['startYear']}-{trend['endYear']}: {keywords1} {keywords2}"
				)
	return output


def overall_summary(company_id: str, start_year: int, end_year: int) -> dict[str, str]:
	extracted_data = extract_data(company_id, start_year, end_year)
	print(extracted_data)
	print()

	output = {}
	for attribute, record in extracted_data.items():
		if not record["years"]:
			output[attribute] = f"No data for {attribute}."
		elif attribute in attribute_map:
			output[attribute] = (
				attribute
				+ ":\n"
				+ "\n".join(
					format_summary(data_summary(record), attribute_map[attribute])
				)
			)
			# else raise NotImplementedError(f"{attribute} summary not implemented")
	return output


if __name__ == "__main__":
	for summary in overall_summary("03824658", 2010, 2023).values():
		print(summary)
		print()
