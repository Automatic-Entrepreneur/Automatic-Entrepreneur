from flask import Flask, render_template, request
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import json
from bs4 import BeautifulSoup as bs
import requests
#import pandas as pd

app = Flask(__name__)


#def index():
    #return render_template('index.html')

def glassdoorScrape(driver, companyName, ret):
    # scraping glassdoor
    
    url = 'https://www.glassdoor.com/Search/results.htm?keyword='+companyName
    
    driver.get(url)
    element = driver.find_element(By.XPATH, "//a[contains(@href, '/Overview/')]")

    #click on the first instance
    driver.execute_script("arguments[0].click();", element)
    
    soup = bs(driver.page_source, 'html.parser')

    # Get Company Mission
    try:
        ret['Mission'] = driver.find_elements(By.XPATH,'.//span[@class="css-dwl48b css-1cnqmgc"]')[1].text
        
    except:
        ret['Mission'] = 'N/A'

    # Get Company Website
    try:
        for i in soup.find(attrs={"data-test": "employer-website"}):
            ret['Website'] = i
    except:
        ret['Website'] = 'N/A'

    # Get Company Industry
    try:
        for i in soup.find(attrs={"data-test": "employer-industry"}):
            ret['Industry'] = i
    except:
        ret['Industry'] = 'N/A'

    # Get Company Headquarters
    try:
        for i in soup.find(attrs={"data-test": "employer-headquarters"}):
            ret['Headquarters'] = i
    except:
        ret['Headquarters'] = 'N/A'

    # Get Company Size
    try:
        for i in soup.find(attrs={"data-test": "employer-size"}):
            ret['Size'] = i
    except:
        ret['Size'] = 'N/A'

    # Get Company Founded
    try:
        for i in soup.find(attrs={"data-test": "employer-founded"}):
            ret['Founded'] = i
    except:
        ret['Founded'] = 'N/A'

    # Get Company Revenue
    try:
        for i in soup.find(attrs={"data-test": "employer-revenue"}):
            rev = i
        if not(rev[1].isnumeric()):
            rev = 'N/A'
    except:
        rev = 'N/A'

    # Get the recommended percentage
    try:
        ret['Recommended to Friends'] = driver.find_elements(By.CLASS_NAME,'textVal')[0].text
    except:
        ret['Recommended to Friends'] = 'N/A'

    # Get CEO approval percentage
    try:
        ret['Approve of CEO']  = driver.find_elements(By.CLASS_NAME, 'textVal')[1].text
    except:
        ret['Approve of CEO']  = 'N/A'

    # Get Rating out of 5
    try:
        ret['Overall Rating'] = driver.find_element(By.XPATH,'.//div[@class="mr-xsm css-1c86vvj eky1qiu0"]').text
    except:
        ret['Overall Rating'] = 'N/A'
    #recommendParagraph = driver.find_element(By.XPATH,'.//div[@class="pb-std pt-std d-none css-ujzx5o e1r4hxna3"]').text

    # Get CEO
    try:
        ceo = driver.find_element(By.XPATH, './/div[@class="d-lg-table-cell ceoName pt-sm pt-lg-0 px-lg-sm css-dwl48b css-1cnqmgc"]').text
        i = 0
        while i < len(ceo):
            if ceo[i].isnumeric():
                ceo = ceo[0:i]
                break
            else:
                i += 1
        ret['CEO'] = ceo.strip()
    except:
        ret['CEO'] = 'N/A'
    # Need to strip numbers at the end

    # Get Company Type
    try:
        for i in soup.find(attrs={"data-test": "employer-type"}):
            typ = i
        if 'Public' in typ:
            dashInd = typ.index('-')
            ticker = typ[dashInd + 10:-1]
        else:
            ticker = 'N/A'
    except:
        typ = 'N/A'

    #script_label = driver.find_element(By.XPATH, "//script[@type = 'text/javascript']").text


    # Look to get more ratings
  
    #ret['Company'] = company
    ret['Company Type'] = typ
    ret['Revenue'] = rev
    ret['Ticker'] = ticker    

def financeScrape(ticker, ret):
    key = 'O8YBYOA6EAO0EANF'

    for i in ['GLOBAL_QUOTE', 'OVERVIEW', 'BALANCE_SHEET', 'INCOME_STATEMENT', 'CASH_FLOW', 'EARNINGS']:
        url = 'https://www.alphavantage.co/query?function='+i+'&symbol='+ticker+'&apikey='+key
        r = requests.get(url)
        data = json.loads(r.text)
        #data = r.json()
        if i == 'GLOBAL_QUOTE':
            quote = data['Global Quote']
            ret['Price'] = quote['05. price']
            ret['Trade Volume (Day)'] = quote['06. volume']
            ret['Change Percentage (Day)'] = quote['10. change percent']
        if i == 'OVERVIEW':
            for k, v in data.items():
                ret[k] = v
        if i == 'BALANCE_SHEET':
            ret['Balance Sheet'] = data["annualReports"]
        if i == 'INCOME_STATEMENT':
            ret['Income Statement'] = data["annualReports"]
        if i == 'CASH_FLOW':
            ret['Cash Flow'] = data["annualReports"]
        if i == 'EARNINGS':
            ret['Annual Earnings'] = data["annualEarnings"]

"""def get_graph(companyName):
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'CompaniesHouse'))
    from CompaniesHouse.CompanySearch import CompanySearch
    from CompaniesHouse import generate_graphs
    from CompaniesHouse import data_util

    companySearch = CompanySearch()
    companyHouseID = companySearch.search(companyName)[0]
    extracted_data = data_util.extract_data(companyHouseID,2010,2022);
    graphName = generate_graphs.generate_bar_graph(extracted_data,companyHouseID)

    return graphName"""

@app.route('/', methods =["GET", "POST"])
def index():
    if request.method == "POST": 
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        #This line prevents the pop-up
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--incognito')

        driver = webdriver.Chrome(options=chrome_options)

        ret = dict()
        companyName = request.form.get("title")

    #    get_graph(companyName)

        glassdoorScrape(driver, companyName, ret)

        if ret['Ticker'] != 'N/A':
            financeScrape(ret['Ticker'], ret)
        else:
            for i in ['Price', 'Description', 'ProfitMargin', '52WeekHigh', '52WeekLow', '50DayMovingAverage', '200DayMovingAverage']:
                ret[i] = 'N/A'
        return ret['CEO']
    return render_template("index.html") 

if __name__=='__main__':
 #   get_graph("Softwire")
    app.run()
