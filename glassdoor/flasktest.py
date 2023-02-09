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
        mission = driver.find_elements(By.XPATH,'.//span[@class="css-dwl48b css-1cnqmgc"]')[1].text
        
    except:
        mission = 'N/A'

    # Get Company Website
    try:
        for i in soup.find(attrs={"data-test": "employer-website"}):
            website = i
    except:
        website = 'N/A'

    # Get Company Industry
    try:
        for i in soup.find(attrs={"data-test": "employer-industry"}):
            industry = i
    except:
        industry = 'N/A'

    # Get Company Headquarters
    try:
        for i in soup.find(attrs={"data-test": "employer-headquarters"}):
            hq = i
    except:
        hq = 'N/A'

    # Get Company Size
    try:
        for i in soup.find(attrs={"data-test": "employer-size"}):
            sz = i
    except:
        sz = 'N/A'

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
        recommended = driver.find_elements(By.CLASS_NAME,'textVal')[0].text
    except:
        recommended = 'N/A'

    # Get CEO approval percentage
    try:
        approveCEO = driver.find_elements(By.CLASS_NAME, 'textVal')[1].text
    except:
        approveCEO = 'N/A'

    # Get Rating out of 5
    try:
        rating = driver.find_element(By.XPATH,'.//div[@class="mr-xsm css-1c86vvj eky1qiu0"]').text
    except:
        rating = 'N/A'
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
        ceo = ceo.strip()
    except:
        ceo = 'N/A'
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
    ret['Mission'] = mission
    ret['Website'] = website
    ret['Headquarters'] = hq
    ret['Size'] = sz
    ret['Industry'] = industry
    ret['Recommended to Friends'] = recommended
    ret['Approve of CEO'] = approveCEO
    ret['Overall Rating'] = rating
    ret['CEO'] = ceo
    ret['Company Type'] = typ
    ret['Founded'] = found
    ret['Revenue'] = rev
    ret['Ticker'] = ticker    

def financeScrape(ticker, ret):
    key = 'O8YBYOA6EAO0EANF'

    for i in ['GLOBAL_QUOTE', 'OVERVIEW']:
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
        glassdoorScrape(driver, companyName, ret)

        if ret['Ticker'] != 'N/A':
            financeScrape(ret['Ticker'], ret)
        else:
            for i in ['Price', 'Description', 'ProfitMargin', '52WeekHigh', '52WeekLow', '50DayMovingAverage', '200DayMovingAverage']:
                ret[i] = 'N/A'
        return ret['CEO']
    return render_template("index.html") 

if __name__=='__main__':
   app.run()