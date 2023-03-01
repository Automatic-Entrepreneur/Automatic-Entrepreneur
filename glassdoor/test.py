import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import json
from bs4 import BeautifulSoup as bs
import requests
import json
import csv

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
            found = i
    except:
        found = 'N/A'

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
        ret['Approve of CEO'] = driver.find_elements(By.CLASS_NAME, 'textVal')[1].text
    except:
        ret['Approve of CEO'] = 'N/A'

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
            ret['Company Type'] = i
        if 'Public' in ret['Company Type']:
            dashInd = ret['Company Type'].index('-')
            ret['Ticker'] = ret['Company Type'][dashInd + 10:-1]
        else:
            ret['Ticker'] = 'N/A'
    except:
        ret['Company Type'] = 'N/A'

    #script_label = driver.find_element(By.XPATH, "//script[@type = 'text/javascript']").text
    # Look to get more ratings
  
    #ret['Company'] = company
    ret['Founded'] = found
    ret['Revenue'] = rev

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
            print('Stock Price: ', ret['Price'])
        if i == 'OVERVIEW':
            for k, v in data.items():
                ret[k] = v
            print(ret['Symbol'])
        if i == 'BALANCE_SHEET':
            ret['Balance Sheet'] = data["annualReports"]
        if i == 'INCOME_STATEMENT':
            ret['Income Statement'] = data["annualReports"]
        if i == 'CASH_FLOW':
            ret['Cash Flow'] = data["annualReports"]
        if i == 'EARNINGS':
            ret['Annual Earnings'] = data["annualEarnings"]

def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    #This line prevents the pop-up
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')

    driver = webdriver.Chrome(options=chrome_options)

    ret = dict()
    companyName = input("Please enter the company name: ")
    glassdoorScrape(driver, companyName, ret)

    if ret['Ticker'] != 'N/A':
        financeScrape(ret['Ticker'], ret)
    
    with open('companyInfo.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(ret.keys())
        w.writerow(ret.values())
