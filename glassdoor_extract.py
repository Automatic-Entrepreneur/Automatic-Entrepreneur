from flask import Flask, render_template, request
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import json
from bs4 import BeautifulSoup as bs
import requests


def glassdoorScrape(driver, companyName, ret):
    # scraping glassdoor
    
    url = 'https://www.glassdoor.com/Search/results.htm?keyword='+companyName
    
    driver.get(url)
    #print('got url')
    element = driver.find_element(By.XPATH, ".//a[contains(@href, '/Overview/')]")
    #print('got overview')
    #click on the first instance
    driver.execute_script("arguments[0].click();", element)
    #print('clicked first')
    #html = driver.page_source
    #file = open("boo.html","w")
    #file.write(html)
    #file.close()
    #for i in range(3): 
    #        sleep(1)
    #        driver.refresh()
    getElements(driver, ret)
    
def getPopupElements(driver, ret):
    try:
        #for i in range(3): 
        #    sleep(2)
        #    driver.refresh()
    
        #driver.find_element(By.XPATH, './/div[@class="css-aztz7y eky1qiu1"]').click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, './/div[@class="css-aztz7y eky1qiu1"]'))).click()
        sleep(3)
        soup = bs(driver.page_source, 'html.parser')
        # Get Extra Ratings
        for cat in ["cultureAndValues", "diversityAndInclusion", "workLife", "seniorManagement", "compAndBenefits", "careerOpportunities"]:
            for i in soup.find(attrs={"data-category":cat}):
                x = str(i)
                x = x[-15:-12]
                j = 0
                while j < len(x):
                    if (not(x[j].isnumeric())):
                        j += 1
                    elif j == 2:
                        x = x[j:]
                        break
                    else:
                        break
                #print(i)
                if cat == "cultureAndValues":
                    ret['Culture & Values Rating'] = x
                #elif cat == "diversityAndInclusion":
                    #ret['Diversity & Inclusion Rating'] = x
                elif cat == "workLife":
                    ret['Work/Life Balance Rating'] = x
                elif cat == "seniorManagement":
                    ret['Senior Management Rating'] = x
                elif cat == "compAndBenefits":
                    ret['Compensation & Benefits Rating'] = x
                elif cat == "careerOpportunities":
                    ret['Career Opportunities Rating'] = x
    except:
        ret['Culture & Values Rating'] = 'N/A'
        #ret['Diversity & Inclusion Rating'] = 'N/A'
        ret['Work/Life Balance Rating'] = 'N/A'
        ret['Senior Management Rating'] = 'N/A'
        ret['Compensation & Benefits Rating'] = 'N/A'
        ret['Career Opportunities Rating'] = 'N/A'

def getElements(driver, ret):
    soup = bs(driver.page_source, 'html.parser')
    #print('got soup')
    # Get Company Name
    try:
        ret['Company'] = driver.find_element(By.XPATH,'.//span[@id="DivisionsDropdownComponent"]').text
        #print('got company')
    except:
        ret['Company'] = 'N/A'
    
        
    # Get Company Mission
    try:
        for i in soup.find(attrs={"data-test": "employerMission"}):
            ret['Mission'] = i
            break
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
    #print(ret['Industry'])

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

    # Get Diversity Rating
    try:
        for i in soup.find(attrs={"data-test": "reviewScoreNumber"}):
            ret['Diversity & Inclusion Rating'] = i
    except:
        ret['Diversity & Inclusion Rating'] = 'N/A'

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
        ret['Ticker'] = 'N/A'
    sleep(5)
        
    getPopupElements(driver, ret)

    #ret['Company'] = company
    ret['Founded'] = found
    ret['Revenue'] = rev

def financeScrape(ticker, ret):
    key = 'O8YBYOA6EAO0EANF'

    for i in ['GLOBAL_QUOTE', 'OVERVIEW', 'BALANCE_SHEET', 'INCOME_STATEMENT', 'CASH_FLOW', 'EARNINGS', 'TIME_SERIES_MONTHLY']:
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
        if i == 'TIME_SERIES_MONTHLY':
            ret['Monthly Time Series'] = data['Monthly Time Series']