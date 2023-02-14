import time

import CompaniesHouse.key
import requests
import json
import pytesseract
import os
import platform
from ixbrlparse import IXBRL
import pickle as pkl
import io
from CompaniesHouse.ScannedReportReader import ScannedReportReader

if platform.system() == 'Darwin':
    pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"
else:
    pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

# Sample Usage:
# company = CompanyInfo('03824658')
# accountInfo = company.getAccountInformation(2022)


class CompanyInfo:
    """
    A class to wrap calls to the Companies House API

    Before usage
    Create a key on the Company House API
    This must be a live key
    Create a new file key.py with a global variable api_key set to your key
    N.B. IP addresses can change on Eduroam!

    Their API does not like changing IP addresses
    You will therefore need to create new keys very frequently!

    Install tesseract
    pytesseract.pytesseract.tesseract_cmd = ##path to tesseract.exe
    """

    # I do not anticipate making anywhere close to this 600 requests so removed the rate limiter

    def __init__(self, company_info):
        """
        :param company_info: The company ID on Company House.
        :type company_info: str
        """
        self.__company_number = company_info
        self.__key = CompaniesHouse.key.api_key
        self.__info = None
        self.__people = None
        self.__accounts = None

    def __fetchInfo(self):
        """
        Function to reduce requests for information
        """
        if not self.__info:
            query = "https://api.company-information.service.gov.uk/company/{}".format(self.__company_number)
            response = requests.get(query, auth=(self.__key, ''))
            self.__info = json.JSONDecoder().decode(response.text)

    def __fetchPeople(self):
        """
        Function to reduce requests for information about people
        """
        if not self.__people:
            query = "https://api.company-information.service.gov.uk/company/{}/officers".format(self.__company_number)
            response = requests.get(query, auth=(self.__key, ''))
            self.__people = json.JSONDecoder().decode(response.text)

    def __fetchAccounts(self):
        """
        Function to reduce requests for information about accounts
        """
        if not self.__info:
            query = "https://api.company-information.service.gov.uk/company/{}/filing-history".format(self.__company_number)
            response = requests.get(query, auth=(self.__key, ''), headers={'category': 'accounts'}, params={'category': 'accounts'})
            self.__accounts = json.JSONDecoder().decode(response.text)['items']

    def allInfo(self):
        """
        :return: "standard" information about the company
        :rtype: dict[str, any]
        """
        self.__fetchInfo()
        return self.__info

    def getName(self):
        """
        :return: the name of the company
        :rtype: str
        """
        self.__fetchInfo()
        return self.__info['company_name']

    def getOffice(self):
        """
        :return: A dictionary containing address of the company office.
        address_line_1: first line of address,
        address_line_2: second line of address,
        locality: city the office is in,
        postal_code: postcode
        :rtype: dict[str, str]
        """
        self.__fetchInfo()
        return self.__info['registered_office_address']

    def dateOfCreation(self):
        """
        :return: The date the company was made in the form "yyyy-mm-dd"
        :rtype: str
        """
        self.__fetchInfo()
        return self.__info['date_of_creation']

    def type(self):
        """
        :return: the type of company
        :rtype: str
        """
        self.__fetchInfo()
        return self.__info['type']

    def currentDirectors(self):
        """
        :return: list of "directors"
        :rtype: list[str]
        """
        self.__fetchPeople()
        return [p['name'] for p in self.__people['items'] if p['officer_role'] == 'director' and 'resigned_on' not in p]

    def currentSecretaries(self):
        """
        :return: list of "secretaries"
        :rtype: list[str]
        """
        self.__fetchPeople()
        return [p['name'] for p in self.__people['items'] if p['officer_role'] == 'secretary' and 'resigned_on' not in p]

    def getAccountHistory(self):
        """
        :return: list of accounts filed by the company
        :rtype: dict[str, any]
        """
        self.__fetchAccounts()
        return self.__accounts

    def getAccountInformation(self, year, pdf_accept=False, pdf_time=10, pdf_pages=50):
        """
        This can be a VERY expensive function.
        It may have to transcribe dozens or even hundreds of pages of pdf.
        It caches as much as possible to reduce load.
        :param year: the year in which the account was filed
        :type year: int
        :param pdf_accept: allows/disallows processing scanned pdfs
        :type pdf_accept: bool
        :param pdf_time: maximum amount of time in s to spend trying to read a scanned pdf
        :type pdf_time: int
        :param pdf_pages: maximum number of pages in a scanned pdf to attempt to read
        :type pdf_pages: int
        :return: list[dict[str, str]]
        """
        dirpath = 'companies_house/{}/{}'.format(self.__company_number, year)
        pklpath = 'companies_house/{}/{}/accounts_{}.pkl'.format(self.__company_number, year, year)
        if os.path.exists(pklpath):
            return pkl.load(open(pklpath, 'rb'))
        self.__fetchAccounts()
        files = sorted((f for f in self.__accounts if f['date'][:4] == str(year) and f['category'] == 'accounts'), key=lambda x: x['date'])
        if not files:
            return []
        file = files[0]
        query = file['links']['document_metadata']
        response = requests.get(query, auth=(self.__key, ''))
        decoded = json.JSONDecoder().decode(response.text)
        query = decoded['links']['document']
        if not os.path.exists(dirpath[:dirpath.index('/')]):
            os.mkdir(dirpath[:dirpath.index('/')])
        if not os.path.exists(dirpath[:dirpath.rindex('/')]):
            os.mkdir(dirpath[:dirpath.rindex('/')])
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        if 'resources' in decoded and 'application/xhtml+xml' in decoded['resources']:
            with requests.get(query, auth=(self.__key, ''), headers={'Accept': 'application/xhtml+xml'}, params={'Accept': 'application/xhtml+xml'}) as response:
                information = [
                    {
                        'name': stat['name'],
                        'value': stat['value'],
                        'unit': stat['unit'],
                        'instant': stat['instant'],
                        'startdate': stat['startdate'],
                        'enddate': stat['enddate'],
                    }
                    for stat in IXBRL(io.StringIO(response.text)).to_table()
                ]
        else:
            if not pdf_accept:
                return []
            t = time.monotonic()
            with requests.get(query, auth=(self.__key, ''), headers={'Accept': 'application/pdf'}, params={'Accept': 'application/pdf'}) as response:
                scanner = ScannedReportReader(response.content, year)
                information = []
                for i in range(min(pdf_pages, len(scanner))):
                    if time.monotonic() - t > pdf_time:
                        break
                    information.extend(scanner.readPage(i))
        pkl.dump(information, open(pklpath, 'wb'))
        return information

    def getLongText(self, year):
        dirpath = 'companies_house/{}/{}'.format(self.__company_number, year)
        pklpath = 'companies_house/{}/{}/accounts_{}.pkl'.format(self.__company_number, year, year)
        if os.path.exists(pklpath):
            return pkl.load(open(pklpath, 'rb'))
        self.__fetchAccounts()
        file = sorted((f for f in self.__accounts if f['date'][:4] == str(year) and f['category'] == 'accounts'), key=lambda x: x['date'])[0]
        query = file['links']['document_metadata']
        response = requests.get(query, auth=(self.__key, ''))
        decoded = json.JSONDecoder().decode(response.text)
        query = decoded['links']['document']
        if not os.path.exists(dirpath[:dirpath.index('/')]):
            os.mkdir(dirpath[:dirpath.index('/')])
        if not os.path.exists(dirpath[:dirpath.rindex('/')]):
            os.mkdir(dirpath[:dirpath.rindex('/')])
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
        if 'resources' in decoded and 'application/xhtml+xml' in decoded['resources']:
            with requests.get(query, auth=(self.__key, ''), headers={'Accept': 'application/xhtml+xml'}, params={'Accept': 'application/xhtml+xml'}) as response:
                d = IXBRL(io.StringIO(response.text))
                return "\n".join([i for i in d.parser.soup.get_text().split("\n") if len(i)>99 and "{" not in i])
        else:
            return ""
