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

if platform.system() == "Darwin":
    pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"
else:
    pytesseract.pytesseract.tesseract_cmd = (
        "C:/Program Files/Tesseract-OCR/tesseract.exe"
    )
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

    Their API does not like changing IP addresses
    You will therefore need to create new keys if you access off university wifi!

    Install tesseract
    pytesseract.pytesseract.tesseract_cmd = ##path to tesseract.exe
    """

    # I do not anticipate making anywhere close to this 600 requests so removed the rate limiter

    def __init__(self, company_info: str) -> None:
        """
        :param company_info: The company ID on Company House.
        :type company_info: str
        """
        self.__company_number = company_info
        self.__key = CompaniesHouse.key.api_key
        self.__info = None
        self.__people = None
        self.__accounts = None
        self.path = os.path.dirname(__file__)

    def __fetch_info(self) -> None:
        """
        Function to reduce requests for information
        """
        if not self.__info:
            query = "https://api.company-information.service.gov.uk/company/{}".format(
                self.__company_number
            )
            response = requests.get(query, auth=(self.__key, ""))
            self.__info = json.JSONDecoder().decode(response.text)

    def __fetch_people(self) -> None:
        """
        Function to reduce requests for information about people
        """
        if not self.__people:
            query = "https://api.company-information.service.gov.uk/company/{}/officers".format(
                self.__company_number
            )
            response = requests.get(query, auth=(self.__key, ""))
            self.__people = json.JSONDecoder().decode(response.text)

    def __fetch_accounts(self) -> None:
        """
        Function to reduce requests for information about accounts
        """
        if not self.__info:
            query = "https://api.company-information.service.gov.uk/company/{}/filing-history".format(
                self.__company_number
            )
            response = requests.get(
                query,
                auth=(self.__key, ""),
                headers={"category": "accounts"},
                params={"category": "accounts"},
            )
            self.__accounts = json.JSONDecoder().decode(response.text)["items"]

    def all_info(self) -> dict[str, any]:
        """
        :return: "standard" information about the company
        :rtype: dict[str, any]
        """
        self.__fetch_info()
        return self.__info

    def get_name(self) -> str:
        """
        :return: the name of the company
        :rtype: str
        """
        self.__fetch_info()
        return self.__info["company_name"]

    def get_office(self) -> dict[str, str]:
        """
        :return: A dictionary containing address of the company office.
        address_line_1: first line of address,
        address_line_2: second line of address,
        locality: city the office is in,
        postal_code: postcode
        :rtype: dict[str, str]
        """
        self.__fetch_info()
        return self.__info["registered_office_address"]

    def date_of_creation(self) -> str:
        """
        :return: The date the company was made in the form "yyyy-mm-dd"
        :rtype: str
        """
        self.__fetch_info()
        return self.__info["date_of_creation"]

    def type(self) -> str:
        """
        :return: the type of company
        :rtype: str
        """
        self.__fetch_info()
        return self.__info["type"]

    def current_directors(self) -> list[str]:
        """
        :return: list of "directors"
        :rtype: list[str]
        """
        self.__fetch_people()
        return [
            p["name"]
            for p in self.__people["items"]
            if p["officer_role"] == "director" and "resigned_on" not in p
        ]

    def current_secretaries(self) -> list[str]:
        """
        :return: list of "secretaries"
        :rtype: list[str]
        """
        self.__fetch_people()
        return [
            p["name"]
            for p in self.__people["items"]
            if p["officer_role"] == "secretary" and "resigned_on" not in p
        ]

    def get_account_history(self) -> dict[str, any]:
        """
        :return: list of accounts filed by the company
        :rtype: dict[str, any]
        """
        self.__fetch_accounts()
        return self.__accounts

    def get_account_information(
            self,
            year: int,
            pdf_accept: bool = True,
            pdf_time: float = 10,
            pdf_pages: int = 50,
    ):
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
        dir_path = os.path.join(
            self.path, "companies_house/{}/{}".format(self.__company_number, year)
        )
        pkl_path = os.path.join(
            self.path,
            "companies_house/{}/{}/accounts_{}.pkl".format(
                self.__company_number, year, year
            ),
        )
        if os.path.exists(pkl_path):
            return pkl.load(open(pkl_path, "rb"))
        self.__fetch_accounts()
        files = sorted(
            (
                f
                for f in self.__accounts
                if f["date"][:4] == str(year) and f["category"] == "accounts"
            ),
            key=lambda x: x["date"],
        )
        if not files:
            return []
        file = files[0]
        query = file["links"]["document_metadata"]
        response = requests.get(query, auth=(self.__key, ""))
        decoded = json.JSONDecoder().decode(response.text)
        query = decoded["links"]["document"]
        if not os.path.exists(os.path.join(self.path, "companies_house")):
            os.mkdir(os.path.join(self.path, "companies_house"))
        if not os.path.exists(
                os.path.join(self.path, "companies_house/{}".format(self.__company_number))
        ):
            os.mkdir(
                os.path.join(
                    self.path, "companies_house/{}".format(self.__company_number)
                )
            )
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        if "resources" in decoded and "application/xhtml+xml" in decoded["resources"]:
            with requests.get(
                    query,
                    auth=(self.__key, ""),
                    headers={"Accept": "application/xhtml+xml"},
                    params={"Accept": "application/xhtml+xml"},
            ) as response:
                information = [
                    {
                        "name": stat["name"],
                        "value": stat["value"],
                        "unit": stat["unit"],
                        "instant": stat["instant"],
                        "startdate": stat["startdate"],
                        "enddate": stat["enddate"],
                    }
                    for stat in IXBRL(io.StringIO(response.text)).to_table()
                ]
        else:
            if not pdf_accept:
                return []
            t = time.monotonic()
            with requests.get(
                    query,
                    auth=(self.__key, ""),
                    headers={"Accept": "application/pdf"},
                    params={"Accept": "application/pdf"},
            ) as response:
                scanner = ScannedReportReader(response.content, year)
                information = []
                for i in range(min(pdf_pages, len(scanner))):
                    if time.monotonic() - t > pdf_time:
                        break
                    information.extend(scanner.readPage(i))
        pkl.dump(information, open(pkl_path, "wb"))
        return information

    def get_long_text(self, year: int) -> str:
        self.__fetch_accounts()
        file = sorted(
            (
                f
                for f in self.__accounts
                if f["date"][:4] == str(year) and f["category"] == "accounts"
            ),
            key=lambda x: x["date"],
        )[0]
        query = file["links"]["document_metadata"]
        response = requests.get(query, auth=(self.__key, ""))
        decoded = json.JSONDecoder().decode(response.text)
        query = decoded["links"]["document"]
        if "resources" in decoded and "application/xhtml+xml" in decoded["resources"]:
            with requests.get(
                    query,
                    auth=(self.__key, ""),
                    headers={"Accept": "application/xhtml+xml"},
                    params={"Accept": "application/xhtml+xml"},
            ) as response:
                d = IXBRL(io.StringIO(response.text))
                return "\n".join(
                    [
                        i
                        for i in d.parser.soup.get_text().split("\n")
                        if len(i) > 99 and "{" not in i
                    ]
                )
        else:
            return ""
