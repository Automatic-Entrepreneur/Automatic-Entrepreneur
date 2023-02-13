import matplotlib.pyplot as plt
from CompaniesHouse.CompanySearch import CompanySearch
from CompaniesHouse.CompanyInfo import CompanyInfo
from data_util import attribute_map, extract_data
import typing


def generate_bar_graph(
        extracted_data: dict[str, dict[str, list[typing.Union[int, float]]]],
        company_id: str,
        show_graph: bool = True,
) -> dict[str, str]:
    # print(extractedData)

    output = {}
    for attribute in extracted_data:
        if len(extracted_data[attribute]["years"]) > 0:
            f, ax = plt.subplots(figsize=(10, 5))
            ax.bar(
                extracted_data[attribute]["years"], extracted_data[attribute]["values"]
            )
            ax.set_title(attribute)
            ax.set_ylabel(f"{attribute_map[attribute][1].title()} in GBP")
            ax.set_xlabel("Year")

            ax.set_ylim([0, max(extracted_data[attribute]["values"]) * 1.2])
            plt.savefig(f"out/{company_id}_{attribute}.png", bbox_inches="tight")
            output[attribute] = f"{company_id}_{attribute}.png"
            if show_graph:
                plt.show()
        else:
            print("No data found for " + attribute)
    return output


if __name__ == "__main__":
    company_id = "02713500"
    start_year = 2010
    end_year = 2023
    extracted_data = extract_data(company_id, start_year, end_year)
    generate_bar_graph(extracted_data, company_id)
