import matplotlib.pyplot as plt
from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo
from data_extraction import extract_data


def generate_bar_graph(extractedData, company_id, show_graph):
    # print(extractedData)

    output = {}
    for attribute in extractedData:
        if len(extractedData[attribute]['years']) > 0:
            f, ax = plt.subplots(figsize=(10, 5))
            ax.bar(extractedData[attribute]['years'], extractedData[attribute]['values'])
            ax.set_ylabel('Profit in GBP')
            ax.set_xlabel('Year')

            ax.set_ylim([0, max(extractedData[attribute]['values']) * 1.2])
            plt.savefig(f'{company_id}_{attribute}.png', bbox_inches='tight')
            output[attribute] = f'{company_id}_{attribute}.png'
            if show_graph:
                plt.show()
        else:
            print('No data found for ' + attribute)
    return output


if __name__ == "__main__":
    extracted_data = extract_data('02713500', 2010, 2023)
    generate_bar_graph(extracted_data, '02713500', show_graph=True)
