import typing

from data_util import trend_map, attribute_map, compare, three_sigfig, extract_data

SHARP_THRESHOLD = 0.15
DRAMATIC_THRESHOLD = 0.7


def data_summary(
    records: dict[str, list[typing.Union[int, float]]]
) -> list[dict[str, typing.Union[int, list[dict[str, typing.Union[int, float]]]]]]:
    values_by_year = list(zip(records["values"], records["years"]))
    prev = values_by_year[0]
    # a list of dictionaries, each one representing a continued profit/loss
    # the "sign" key indicates profit/loss/neither
    # the "trends" key points to a list of dictionaries, each one representing a continuous increase/decrease
    trends_list = [
        {
            "sign": compare(prev[0], 0),
            "trends": [
                {
                    "trend": 0,
                    "startVal": prev[0],
                    "endVal": prev[0],
                    "startYear": prev[1],
                    "endYear": prev[1],
                }
            ],
        }
    ]

    for value, year in values_by_year[1:]:
        sign = compare(value, 0)
        trend = compare(value, prev[0])
        if trends_list[-1]["sign"] == sign or sign == 0:
            trends = trends_list[-1]["trends"]
            if trends[-1]["trend"] == trend:
                trends[-1]["endVal"] = value
                trends[-1]["endYear"] = year
            else:
                trends.append(
                    {
                        "trend": trend,
                        "startVal": prev[0],
                        "endVal": value,
                        "startYear": prev[1],
                        "endYear": year,
                    }
                )
        else:
            trends_list.append(
                {
                    "sign": sign,
                    "trends": [
                        {
                            "trend": trend,
                            "startVal": prev[0],
                            "endVal": value,
                            "startYear": prev[1],
                            "endYear": year,
                        }
                    ],
                }
            )
        prev = (value, year)
    return trends_list


def format_summary(
    values_by_year: list[
        dict[str, typing.Union[int, list[dict[str, typing.Union[int, float]]]]]
    ],
    sign_map: dict[int, str],
) -> list[str]:
    output = []
    for section in values_by_year:
        for trend in section["trends"]:
            if trend["startYear"] != trend["endYear"]:
                s = section["sign"]
                t = s * trend["trend"]
                if trend["startVal"] == 0:
                    gradient_word = "sharply"
                else:
                    duration = trend["endYear"] - trend["startYear"]
                    gradient = (
                        abs((trend["startVal"] - trend["endVal"]) / trend["startVal"])
                        / duration
                    )
                    gradient_percent = f"by {three_sigfig(gradient * 100)}% per year"
                    gradient_word = f"gradually {gradient_percent}"
                    if gradient >= SHARP_THRESHOLD:
                        gradient_word = f"sharply {gradient_percent}"
                    if gradient >= DRAMATIC_THRESHOLD:
                        gradient_word = f"dramatically {gradient_percent}"
                keywords1 = sign_map[s]
                if s != 0:
                    keywords1 += " " + trend_map[t]
                    if t != 0:
                        keywords1 += " " + gradient_word
                keywords2 = (
                    f"at {three_sigfig(trend['startVal'], True)} GBP."
                    if t == 0
                    else f"from {three_sigfig(trend['startVal'], True)} to {three_sigfig(trend['endVal'], True)} GBP."
                )
                output.append(
                    f"{trend['startYear']}-{trend['endYear']}: {keywords1} {keywords2}"
                )
    return output


def overall_summary(
    extracted_data: dict[str, dict[str, list[typing.Union[int, float]]]]
) -> dict[str, list[str]]:
    output = {}
    for attribute, record in extracted_data.items():
        if not record["years"]:
            output[attribute] = f"No data for {attribute}."
        elif attribute in attribute_map:
            output[attribute] = format_summary(
                data_summary(record), attribute_map[attribute]
            )
            # else raise NotImplementedError(f"{attribute} summary not implemented")
    return output


if __name__ == "__main__":
    company_id = "09289164"
    start_year = 2010
    end_year = 2023

    data = extract_data(company_id, start_year, end_year)["data"]
    print(data)
    print()

    for label, summaries in overall_summary(data).items():
        print(label + ":\n" + "\n".join(summaries))
        print()
