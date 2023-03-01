import typing
import matplotlib.pyplot as plt
from matplotlib import ticker
from bokeh.embed import file_html, components, autoload_static
from bokeh.plotting import figure
from bokeh.resources import INLINE

from data_util import attribute_map, extract_data

test_data = {
    "FixedAssets": {
        "years": [2021, 2020, 2019, 2018, 2017, 2016],
        "values": [2895, 3526, 4367, 5488, 5062, 6538],
    },
    "CurrentAssets": {
        "years": [2021, 2020, 2019, 2018, 2017, 2016],
        "values": [91263, 100764, 139282, 107284, 174721, 127186],
    },
    "ProfitLoss": {
        "years": [2021, 2020, 2019, 2018, 2017, 2016],
        "values": [15000, 13000, 17000, 19000, 20000, 25000],
    }
}


def generate_bar_graph(
        extracted_data: dict[str, dict[str, list[typing.Union[int, float]]]],
        path: str,
        company_id: str,
        show_graph: bool = True,
) -> dict[str, str]:
    # print(extractedData)

    plt.style.use("seaborn")

    output = {}
    for attribute in extracted_data:
        if len(extracted_data[attribute]["years"]) > 0:
            f, ax = plt.subplots(figsize=(8, 5))

            ax.set_axisbelow(True)
            plt.grid(axis="y", alpha=0.5)

            ax.bar(
                extracted_data[attribute]["years"],
                extracted_data[attribute]["values"],
                width=0.6,
            )
            ax.set_title(attribute)
            ax.set_ylabel(f"{attribute_map[attribute][1].title()} in GBP")
            ax.set_xlabel("Year")

            ax.yaxis.labelpad = 10
            ax.get_yaxis().set_major_formatter(
                ticker.FuncFormatter(lambda y, p: format(int(y), ","))
            )

            ax.set_ylim([min(0, min(extracted_data[attribute]["values"])), max(extracted_data[attribute]["values"]) * 1.2])
            plt.savefig(f"{path}{company_id}_{attribute}.png", bbox_inches="tight")
            output[attribute] = f"{path}{company_id}_{attribute}.png"

            if show_graph:
                plt.show()
        else:
            print("No data found for " + attribute)
    return output


def generate_bar_graph_bokeh(
        extracted_data: dict[str, dict[str, list[typing.Union[int, float]]]]
) -> dict[str, dict[str, str]]:
    output = {}
    for attribute in extracted_data:
        if len(extracted_data[attribute]["years"]) > 0:
            fig = figure(width=700, height=500,
                         title=attribute,
                         x_axis_label="Year",
                         y_axis_label=f"{attribute_map[attribute][1].title()} in GBP")

            fig.vbar(
                x=test_data[attribute]["years"],
                width=0.5,
                bottom=0,
                top=test_data[attribute]["values"],
                color='lightsteelblue'
            )

            script, div = components(fig)
            output[attribute] = {"script": script,
                                 "div": div}

        else:
            print("No data found for " + attribute)

    output["js_resources"] = INLINE.render_js()

    return output


if __name__ == "__main__":
    # company_id = "02713500"
    # start_year = 2010
    # end_year = 2023
    # extracted_data = extract_data(company_id, start_year, end_year)["data"]
    # generate_bar_graph(extracted_data, "", company_id)

    bokeh_output = generate_bar_graph_bokeh(test_data)

    file = open("bokeh_output.html", 'w')

    file.write("<!doctype html>")
    file.write("<html lang=\"en\">")
    file.write("<head>")
    file.write("<meta charset=\"utf-8\">")
    file.write("<meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\">")
    file.write("<title>Embed Demo</title>")
    file.write(bokeh_output["js_resources"])
    # file.write("<link rel=\"stylesheet\" "
    #            "href=\"http://cdn.bokeh.org/bokeh/release/bokeh-2.4.10.min.css\" "
    #            "type=\"text/css\"/>")
    # file.write("<script type=\"text/javascript\" "
    #            "src=\"http://cdn.bokeh.org/bokeh/release/bokeh-2.4.10.min.js\">"
    #            "</script>")
    for attribute in bokeh_output:
        if attribute != "js_resources":
            file.write(bokeh_output[attribute]["script"])
    file.write("</head>")
    file.write("<body>")
    file.write("<h3>header</h3>")
    file.write("<div class='bokeh'>")
    for attribute in bokeh_output:
        if attribute != "js_resources":
            file.write(bokeh_output[attribute]["div"])
    file.write("</div>")
    file.write("</body>")
    file.write("</html>")

    file.close()
