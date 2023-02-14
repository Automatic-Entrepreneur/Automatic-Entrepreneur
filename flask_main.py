from flask import Flask, render_template, request
from selenium import webdriver
from glassdoor_extract import glassdoorScrape, financeScrape
from CompaniesHouse.CompanySearch import CompanySearch

app = Flask(__name__)

def get_(companyName):
    companySearch = CompanySearch()
    return companySearch.search(companyName)[0]['company_number']

def get_CEO(companyName):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        #This line prevents the pop-up
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--incognito')

        driver = webdriver.Chrome(options=chrome_options)

        ret = dict()

        glassdoorScrape(driver, companyName, ret)

        if ret['Ticker'] != 'N/A':
            financeScrape(ret['Ticker'], ret)
        else:
            for i in ['Price', 'Description', 'ProfitMargin', '52WeekHigh', '52WeekLow', '50DayMovingAverage', '200DayMovingAverage']:
                ret[i] = 'N/A'
        return ret['CEO']

@app.route('/', methods =["GET", "POST"])
def index():
    if request.method == "POST":
        companyName = request.form.get("title")
        return get_CEO(companyName)
    return render_template("index.html") 

if __name__=='__main__':
    app.run()
