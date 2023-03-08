import requests
import json
import csv

"""Need to input ticker/symbol instead of company name"""


def financeScrape(ticker, ret):
    key = "O8YBYOA6EAO0EANF"

    for i in [
        "GLOBAL_QUOTE",
        "OVERVIEW",
        "BALANCE_SHEET",
        "INCOME_STATEMENT",
        "CASH_FLOW",
        "EARNINGS",
        "TIME_SERIES_MONTHLY",
    ]:
        url = (
            "https://www.alphavantage.co/query?function="
            + i
            + "&symbol="
            + ticker
            + "&apikey="
            + key
        )
        r = requests.get(url)
        data = json.loads(r.text)
        # data = r.json()
        if i == "GLOBAL_QUOTE":
            quote = data["Global Quote"]
            ret["Price"] = quote["05. price"]
            ret["Trade Volume (Day)"] = quote["06. volume"]
            ret["Change Percentage (Day)"] = quote["10. change percent"]
            print("Stock Price: ", ret["Price"])
        if i == "OVERVIEW":
            for k, v in data.items():
                ret[k] = v
            print(ret["Symbol"])
        if i == "BALANCE_SHEET":
            ret["Balance Sheet"] = data["annualReports"]
        if i == "INCOME_STATEMENT":
            ret["Income Statement"] = data["annualReports"]
        if i == "CASH_FLOW":
            ret["Cash Flow"] = data["annualReports"]
        if i == "EARNINGS":
            ret["Annual Earnings"] = data["annualEarnings"]
        if i == "TIME_SERIES_MONTHLY":
            ret["Monthly Time Series"] = data["Monthly Time Series"]


def main():
    ticker = input("Input Ticker: ")
    ret = dict()
    financeScrape(ticker, ret)
    """with open('alphavantage.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(ret.keys())
        w.writerow(ret.values())"""
    return ret


if __name__ == "__main__":
    import time

    tic = time.perf_counter()
    main()
    toc = time.perf_counter()
    print(f"Code ran in {toc - tic:0.4f} seconds")
