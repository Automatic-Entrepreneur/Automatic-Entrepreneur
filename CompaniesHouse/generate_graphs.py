import matplotlib.pyplot as plt
from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo

def preprocessing():
    print()

def bar_graph(x,y):
    menMeans = y

    # Creating a figure with some fig size
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x, menMeans, width=0.4)
    # Now the trick is here.
    # plt.text() , you need to give (x,y) location , where you want to put the numbers,
    # So here index will give you x pos and data+1 will provide a little gap in y axis.
    for index, data in enumerate(menMeans):
        plt.text(x=index, y=data + 1, s=f"{data}", fontdict=dict(fontsize=20))
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    company = CompanyInfo('03824658')
    accountInfo = company.getAccountInformation(2022)
    extractedData = {'ProfitLoss':
                         {'years':[],'values':[]},
                     'FixedAssets':
                         {'years':[],'values':[]},
                     'CurrentAssets':
                         {'years':[],'values':[]}}

    for year in range(2018, 2023):
        accountInfo = company.getAccountInformation(year)

        for record in accountInfo:
            for attribute in extractedData.keys():
                if record['name'] == attribute:
                    if record['startdate'] == None:
                        time = int(record['instant'][0:4])
                    else:
                        time = int(record['startdate'][0:4])

                    extractedData[attribute]['values'].append(record['value'])
                    extractedData[attribute]['years'].append(time)

               #     print(record['startdate'])
                #    print(extractedData[attribute], year)
                    break

    print(extractedData)
    plt.bar(extractedData['CurrentAssets']['years'],extractedData['CurrentAssets']['values'])
    plt.ylabel('Profit in GBP')
    plt.xlabel('Year')

    plt.ylim([0, max(extractedData['CurrentAssets']['values']) * 1.2])

    plt.show()

  #  bar_graph(years,extractedData['ProfitLoss'])

    print(accountInfo)
