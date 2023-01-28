from googlesearch import search
import requests
import json
import pickle as pkl
import key


class TooManyResults(UserWarning):
    def __init__(self, msg='Number of results for CompanySearch must be ≤ 20'):
        super().__init__(msg)


class CompanySearch:
    def __init__(self):
        self.__key = key.api_key

    def search(self, company_name, n=5):
        """
        Searches query on google and companies house
        :param query: company to search for
        :type query: str
        :param n: number of results
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
        # return ['date_of_creation'] is the date the company was created on yyyy-mm-dd
        # Optional:
        # return['date_of_cessation'] the date the company closed on yyyy-mm-dd
        # return['registered_office_address'] a dictionary containing the office address of the company:
        # return['sic_codes'] a list of unique identifiers for what the company does
        # return['industry'] a list of strings describing what the company does
        if n > 20:
            raise ResourceWarning
        searched_companies = search(company_name, extra_params={'as_sitesearch': 'find-and-update.company-information.service.gov.uk/company'}, country='en', num=n, stop=n)
        ids_for_CH = [next(searched_companies)[67:75] for _ in range(n)]
        query = "https://api.company-information.service.gov.uk/advanced-search/companies"
        params = {'company_name_includes': company_name}
        results = json.JSONDecoder().decode(requests.get(query, auth=(self.__key, ''), params=params).text)['items']
        companies = {
            company['company_number']: {
                'company_name': company['company_name'],
                'company_number': company['company_number'],
                'company_status': company['company_status'],
                'company_type': company['company_type'],
                'date_of_creation': company['date_of_creation'],
            }
            for company in results
        }
        for company in results:
            if 'date_of_cessation' in company:
                companies[company['company_number']]['date_of_cessation'] = company['date_of_cessation']
            if 'registered_office_address' in company:
                companies[company['company_number']]['registered_office_address'] = company['registered_office_address']
            if 'sic_codes' in company:
                companies[company['company_number']]['sic_codes'] = company['sic_codes']
        no_info = set(ids_for_CH) - companies.keys()
        for company in no_info:
            query = "https://api.company-information.service.gov.uk/company/{}".format(company)
            profile = json.JSONDecoder().decode(requests.get(query, auth=(self.__key, ''), params=params).text)
            companies[company] = {
                'company_name': profile['company_name'],
                'company_number': profile['company_number'],
                'company_status': profile['company_status'],
                'company_type': profile['type'],
                'date_of_creation': profile['date_of_creation'],
            }
            if 'date_of_cessation' in profile:
                companies[company]['date_of_cessation'] = profile['date_of_cessation']
            if 'registered_office_address' in profile:
                companies[company]['registered_office_address'] = profile['registered_office_address']
            if 'sic_codes' in profile:
                companies[company]['sic_codes'] = profile['sic_codes']
        codes_to_text = pkl.load(open('sic_codes.pkl', 'rb'))
        for company in companies.values():
            if 'sic_codes' in company:
                 company['industry'] = [codes_to_text[sic] for sic in company['sic_codes']]
        seen = set()
        search_results = []
        for id in ids_for_CH:
            if id not in seen:
                seen.add(id)
                search_results.append(companies[id])
        for id, company in companies.items():
            if id not in seen:
                seen.add(id)
                search_results.append(company)
        return search_results

