import matplotlib.pyplot as plt
from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo
from data_extraction import extract_data


def generate_bar_graph(company_id):
    extractedData = extract_data(company_id, 2010, 2023)
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
