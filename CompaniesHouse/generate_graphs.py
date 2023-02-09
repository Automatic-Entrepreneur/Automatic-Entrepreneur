import matplotlib.pyplot as plt
from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo


def generate_bar_graph(company_id):
    company = CompanyInfo(company_id)
    extractedData = {'ProfitLoss':
                         {'years': [], 'values': [], },
                     'FixedAssets':
                         {'years': [], 'values': []},
                     'CurrentAssets':
                         {'years': [], 'values': []}}

    for year in range(2010, 2023):
        try:
            accountInfo = company.getAccountInformation(year)
            print(accountInfo)
        except IndexError:
            continue
        except NotImplementedError:  # Risky behaviour - how to indicate the graph isn't there
            continue

        for record in accountInfo:
            for attribute in extractedData.keys():
                if record['name'] == attribute:
                    if record['startdate'] == None:
                        time = int(record['instant'][0:4])
                    else:
                        time = int(record['startdate'][0:4])

                    extractedData[attribute]['values'].append(record['value'])
                    extractedData[attribute]['years'].append(time)
                    break
    print(extractedData)
    for attribute in extractedData.keys():
        if len(extractedData[attribute]['years']) > 0:
            plt.bar(extractedData[attribute]['years'], extractedData[attribute]['values'])
            plt.ylabel('Profit in GBP')
            plt.xlabel('Year')

            plt.ylim([0, max(extractedData[attribute]['values']) * 1.2])

            plt.show()
        else:
            print('No data found for ' + attribute)

if __name__ == "__main__":
    generate_bar_graph('02713500')