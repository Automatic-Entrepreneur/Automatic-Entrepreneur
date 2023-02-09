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
                        record_year = int(record['instant'][0:4])
                    else:
                        record_year = int(record['startdate'][0:4])

                    if record_year not in extractedData[attribute]['years']:
                        extractedData[attribute]['values'].append(record['value'])
                        extractedData[attribute]['years'].append(record_year)
                    else:
                        i = extractedData[attribute]['years'].index(record_year)
                        extractedData[attribute]['values'][i] = max(extractedData[attribute]['values'][i], record['value'])

                    break

    # print(extractedData)
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