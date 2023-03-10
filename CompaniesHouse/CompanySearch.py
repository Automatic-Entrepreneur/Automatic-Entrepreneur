import json
import os
import pickle as pkl
from functools import lru_cache

import requests

import CompaniesHouse.key


class TooManyResults(UserWarning):
    """
    To be raised when a search requests more than 500 companies
    """

    def __init__(self, msg="Number of results for CompanySearch must be ≤ 500"):
        super().__init__(msg)


class CompanySearch:
    """
    A class to wrap searches for companies on CompaniesHouse
    """

    def __init__(self):
        self.__key = CompaniesHouse.key.api_key
        self.path = os.path.dirname(__file__)

    @lru_cache(maxsize=5)
    def search(
        self, company_name: str, active: bool = True, start: int = 0, n: int = 20
    ) -> list[dict[str, str]]:
        """
        Searches query on companies house
        :param company_name: company to search for
        :type company_name: str
        :param active: if true search only shows results for active companies
        :type active: bool
        :param start: position of the first result (used for multiple pages)
        :type start: int
        :param n: maximum number of results
        :type n: int
        :return: ordered list of potential matches
        :rtype: list[dict[str, str]]
        :exception TooManyResults: if n > 20 to avoid google blocking IP
        """
        # The return is a list of results (dictionaries) each with attributes
        # Necessary:
        # return['company_name'] is the name of the company
        # return['company_number'] is the Companies House ID for the company
        # return['company_status'] is the status of the company ie active/dissolved/...
        # return['company_type'] is the type of the company ie ltd/private/...
        # Optional:
        # return ['date_of_creation'] is the date the company was created on yyyy-mm-dd (almost always present)
        # return['date_of_cessation'] the date the company closed on yyyy-mm-dd
        # return['registered_office_address'] a dictionary containing the office address of the company:
        # return['sic_codes'] a list of unique identifiers for what the company does
        # return['industry'] a list of strings describing what the company does
        if n > 500:
            raise TooManyResults
        query = (
            "https://api.company-information.service.gov.uk/advanced-search/companies"
        )
        params = {
            "company_name_includes": company_name,
            "start_index": start,
            "size": n,
        }
        if active:
            params["company_status"] = "active"
        results = json.JSONDecoder().decode(
            requests.get(query, auth=(self.__key, ""), params=params).text
        )["items"]
        companies = {
            company["company_number"]: {
                "company_name": company["company_name"],
                "company_number": company["company_number"],
                "company_status": company["company_status"],
                "company_type": company["company_type"],
            }
            for company in results
        }
        for company in results:
            if "date_of_creation" in company:
                companies[company["company_number"]]["date_of_creation"] = company[
                    "date_of_creation"
                ]
            if "date_of_cessation" in company:
                companies[company["company_number"]]["date_of_cessation"] = company[
                    "date_of_cessation"
                ]
            if "registered_office_address" in company:
                companies[company["company_number"]][
                    "registered_office_address"
                ] = company["registered_office_address"]
            if "sic_codes" in company:
                companies[company["company_number"]]["sic_codes"] = company["sic_codes"]
        codes_to_text = pkl.load(open(os.path.join(self.path, "sic_codes.pkl"), "rb"))
        for company in companies.values():
            if "sic_codes" in company:
                company["industry"] = [
                    codes_to_text[sic]
                    for sic in company["sic_codes"]
                    if sic in codes_to_text
                ]
        return sorted(
            companies.values(),
            key=lambda x: x["date_of_creation"]
            if "date_of_creation" in x
            else "9999-99-99",
        )
