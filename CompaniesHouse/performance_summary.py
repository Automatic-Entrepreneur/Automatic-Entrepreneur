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
) -> list[dict[str, int | list[list[int]]]]:
	values_by_year = list(zip(records["values"], records["years"]))
	prev = values_by_year[0]
	trend_list = [{"sign": compare(prev[0], 0), "trend": [[0, prev[1], prev[1]]]}]

	for value, year in values_by_year[1:]:
		sign = compare(value, 0)
		direction = compare(value, prev[0])
		if trend_list[-1]["sign"] == sign or sign == 0:
			trends = trend_list[-1]["trend"]
			if trends[-1][0] == direction:
				trends[-1][2] = year
			else:
				trends.append([direction, prev[1], year])
		else:
			trend_list.append({"sign": sign, "trend": [[direction, prev[1], year]]})
		prev = (value, year)
	return trend_list


def format_summary(
		values_by_year: list[dict[str, int | list[list[int]]]], sign_map: dict[int, str]
) -> str:
	output = []
	for section in values_by_year:
		for trend in section["trend"]:
			if trend[1] != trend[2]:
				s = section["sign"]
				if s != 0:
					keywords = f"{trend_map[s * trend[0]]} {sign_map[s]}"
				else:
					keywords = sign_map[s]
				output.append(f"There was {keywords} from {trend[1]} to {trend[2]}.")
	return "\n".join(output)


def overall_summary(company_id: str, start_year: int, end_year: int) -> dict[str, str]:
	extracted_data = extract_data(company_id, start_year, end_year)
	print(extracted_data)
	print()

	output = {}
	for attribute, record in extracted_data.items():
		if not record["years"]:
			output[attribute] = f"No data for {attribute}."
		elif attribute in attribute_map:
			output[attribute] = attribute + ":\n" + format_summary(data_summary(record), attribute_map[attribute])
			# else raise NotImplementedError(f"{attribute} summary not implemented")
	return output


if __name__ == "__main__":
	for summary in overall_summary("02713500", 2010, 2023).values():
		print(summary)
		print()
