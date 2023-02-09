from CompaniesHouse.CompanyInfo import CompanyInfo

trend_map = {1: "increasing", -1: "decreasing", 0: "steady"}

attribute_map = {
	"ProfitLoss": {1: "profit", -1: "loss", 0: "no profit or loss"},
	"FixedAssets": {
		1: "value of fixed assets",
		-1: "NEGATIVE value of fixed assets",
		0: "no change in the value of fixed assets",
	},
	"CurrentAssets": {
		1: "value of current assets",
		-1: "NEGATIVE value of current assets",
		0: "no change in the value of current assets",
	},
}


def extract_data(
		company_id: str,
		start_year: int,
		end_year: int,
) -> dict[str, dict[str, list[int | float]]]:
	company = CompanyInfo(company_id)

	extracted_data = {}
	for attribute in attribute_map:
		extracted_data[attribute] = {}

	for year in range(start_year, end_year):
		try:
			account_info = company.getAccountInformation(year)
			print(account_info)
		except IndexError:
			continue
		except NotImplementedError:  # Risky behaviour - how to indicate the graph isn't there
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

	return output
