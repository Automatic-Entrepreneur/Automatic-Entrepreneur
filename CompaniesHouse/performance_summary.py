from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo


keywords = {"+": "increased", "-": "decreased", "=": "stayed the same"}


def summary(company_id: str) -> tuple[list[str], list[int]]:
	company = CompanyInfo(company_id)
	profit_by_year = [
		(record["value"], year - 1)
		for year in range(2018, 2023)
		for record in company.getAccountInformation(year)
		if record["name"] == "ProfitLoss" and record["startdate"] == f"{year - 1}-01-01"
	]

	start = profit_by_year[0]
	prev = profit_by_year[1]
	if prev[0] > start:
		trend = [keywords["+"]]
	elif prev[0] == start:
		trend = [keywords["="]]
	else:
		trend = [keywords["-"]]
	groups = [[start[1], prev[1]]]
	for profit, year in profit_by_year[2:]:
		if trend[-1] == keywords["+"]:
			if profit > prev[0]:
				groups[-1] = year
			else:
				trend.append(keywords["-"]) if profit < prev[0] else trend.append(keywords["="])
				groups.append([year, None])
		elif trend[-1] == keywords["-"]:
			if profit < prev[0]:
				groups[-1] = year
			else:
				trend.append(keywords["+"]) if profit > prev[0] else trend.append(keywords["="])
				groups.append([year, None])
		else:
			if profit == prev[0]:
				groups[-1] = year
			else:
				trend.append(keywords["+"]) if profit > prev[0] else trend.append(keywords["-"])
				groups.append([year, None])
		prev = (profit, year)

	return trend, groups


if __name__ == "__main__":
	print(summary("03824658"))
