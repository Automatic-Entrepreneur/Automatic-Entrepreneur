
# Everything in CompaniesHouse is wrapped in two classes.

- CompanyInformation
  This is a class which wraps API calls and extraction from accounts.
  It is well-documented.

- CompanySearch
  This class performs searches for a company name, returning an ordered list of *at most 20* results.

  Each result contains the company and some brief information.
  - The results are ordered -- the top few are the most relevant -- the rest are likely to be largely unrelated.
  - I use the top n results on google (5 by default) to order the top companies
    If this is problematic, tell me (Harry). This search is by nature time consuming and Google or CH will IP block if we do too many.