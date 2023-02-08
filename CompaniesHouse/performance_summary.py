from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo


keywords = {1: "increased", -1: "decreased", 0: "stayed the same"}


def ternary(n: int) -> int:
	if n > 0:
		return 1
	elif n < 0:
		return -1
	else:
		return 0


def summary(company_id: str) -> tuple[list[int], list[list[int]]]:
	"""
	company = CompanyInfo(company_id)
	profit_by_year = [
		(record["value"], year - 1)
		for year in range(2018, 2023)
		for record in company.getAccountInformation(year)
		if record["name"] == "ProfitLoss" and record["startdate"] == f"{year - 1}-01-01"
	]
	"""

	profit_by_year = [(600, 2017), (700, 2018), (100, 2019), (50, 2020), (50, 2021), (500, 2022)]

	start = profit_by_year[0]
	prev = profit_by_year[1]

	trend_list = [ternary(prev[0] - start[0])]
	groups = [[start[1], prev[1]]]

	for profit, year in profit_by_year[2:]:
		trend = ternary(profit - prev[0])
		if trend_list[-1] == trend:
			groups[-1][-1] = year
		else:
			trend_list.append(trend)
			groups.append([prev[1], year])
		prev = (profit, year)

	return trend_list, groups


if __name__ == "__main__":
	trends, intervals = summary("03824658")
	output = [
		f"Profit {keywords[trend]} from {start} to {end}."
		for trend, (start, end) in zip(trends, intervals)
	]
	print(" ".join(output))

