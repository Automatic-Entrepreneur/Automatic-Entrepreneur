from data_util import trend_map, attribute_map, compare, three_sigfig, extract_data

GRADIENT_THRESHOLD = 0.15


def data_summary(
		records: dict[str, list[int | float]]
) -> list[dict[str, int | list[dict[str, int | float]]]]:
	values_by_year = list(zip(records["values"], records["years"]))
	prev = values_by_year[0]
	# a list of dictionaries, each one representing a continued profit/loss
	# the "sign" key indicates profit/loss/neither
	# the "trends" key points to a list of dictionaries, each one representing a continuous increase/decrease
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
				gradient = abs(trend["startVal"] - trend["endVal"]) / trend["startVal"]
				gradient_word = "sharply" if gradient >= GRADIENT_THRESHOLD else "slightly"
				keywords1 = (
					f"{sign_map[s]}" if s == 0 else f"{sign_map[s]} {trend_map[t]} {gradient_word} by {three_sigfig(gradient * 100)}%"
				)
				keywords2 = (
					f"at {three_sigfig(trend['startVal'])} GBP."
					if t == 0
			else f"from {three_sigfig(trend['startVal'])} to {three_sigfig(trend['endVal'])} GBP."
				)
				output.append(
					f"{trend['startYear']}-{trend['endYear']}: {keywords1} {keywords2}"
				)
	return output


def overall_summary(
		extracted_data: dict[str, dict[str, list[int | float]]]
) -> dict[str, list[str]]:
	output = {}
	for attribute, record in extracted_data.items():
		if not record["years"]:
			output[attribute] = f"No data for {attribute}."
		elif attribute in attribute_map:
			output[attribute] = format_summary(
				data_summary(record), attribute_map[attribute]
			)
			# else raise NotImplementedError(f"{attribute} summary not implemented")
	return output


if __name__ == "__main__":
	company_id = "03824658"
	start_year = 2010
	end_year = 2023

	data = extract_data(company_id, start_year, end_year)
	print(data)
	print()

	for label, summaries in overall_summary(data).items():
		print(label + ":\n" + "\n".join(summaries))
		print()
