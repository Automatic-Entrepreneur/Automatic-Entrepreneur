from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo


def compare(a: float, b: float) -> int:
	if a > b:
		return 1
	elif a < b:
		return -1
	else:
		return 0


def summary(company_id: str) -> list[dict[str, int | list[list[int]]]]:
	"""
	company = CompanyInfo(company_id)
	profit_by_year = [
		(record["value"], year - 1)
		for year in range(2018, 2023)
		for record in company.getAccountInformation(year)
		if record["name"] == "ProfitLoss" and record["startdate"] == f"{year - 1}-01-01"
	]
	"""

	profitloss_by_year = [
		(0, 2015),
		(0, 2016),
		(50, 2017),
		(50, 2018),
		(100, 2019),
		(200, 2020),
		(-55, 2021),
		(-25, 2022),
		(-25, 2023)
	]

	prev = profitloss_by_year[0]
	trend_list = [{
		"is_profit": compare(prev[0], 0),
		"trend": [[0, prev[1], prev[1]]]
	}]

	for profitloss, year in profitloss_by_year[1:]:
		is_profit = compare(profitloss, 0)
		direction = compare(profitloss, prev[0])
		if trend_list[-1]["is_profit"] == is_profit or is_profit == 0:
			trends = trend_list[-1]["trend"]
			if trends[-1][0] == direction:
				trends[-1][2] = year
			else:
				trends.append([direction, prev[1], year])
		else:
			trend_list.append({
				"is_profit": is_profit,
				"trend": [[direction, prev[1], year]]
			})

		prev = (profitloss, year)

	return trend_list


if __name__ == "__main__":
	trend_words = {1: "increasing", -1: "decreasing", 0: "steady"}
	profit_words = {1: "profit", -1: "loss", 0: "no change"}
	summary = summary("03824658")
	output = []
	for section in summary:
		for trend in section["trend"]:
			if trend[1] != trend[2]:
				p = section['is_profit']
				if p != 0:
					keywords = f"{trend_words[p * trend[0]]} {profit_words[p]}"
				else:
					keywords = "no profit or loss"
				output.append(
					f"There was {keywords} from {trend[1]} to {trend[2]}."
				)
	print("\n".join(output))

