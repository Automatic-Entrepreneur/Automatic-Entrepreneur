import matplotlib.pyplot as plt
from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo

def preprocessing():
    print()

def graph():
    plt.plot([1, 2, 3, 4])
    plt.ylabel('some numbers')
    plt.show()

if __name__ == "__main__":
    company = CompanyInfo('03824658')
    accountInfo = company.getAccountInformation(2022)
    extractedData = {'ProfitLoss':[],'FixedAssets':[],'CurrentAssets':[]}
    years = []

    for year in range(2018, 2023):
        accountInfo = company.getAccountInformation(year)

        for record in accountInfo:
            for attribute in extractedData.keys():
                if record['name'] == attribute and record['startdate'] == str(year-1)+'-01-01':
                    extractedData[attribute].append(record['value'])
                    years.append(year-1)
                    print(record['startdate'])
                    print(extractedData[attribute], year)
                    break

    plt.plot(years,extractedData['ProfitLoss'])
    plt.ylabel('Profit GBP')
    plt.show()
    print(accountInfo)
