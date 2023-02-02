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
    turnover = []
    years = []

    for year in range(2018, 2023):
        accountInfo = company.getAccountInformation(year)

        for record in accountInfo:
            if record['name'] == 'ProfitLoss':
                turnover.append(record['value'])
                years.append(year)
                print(turnover, year)
                break

    plt.plot(years,turnover)
    plt.ylabel('Profit GBP')
    plt.show()
    print(accountInfo)
