
# Everything in CompaniesHouse is wrapped in two classes.

Documentation for these is in the code

- CompanyInformation
  - This is a class which wraps API calls and extraction from accounts.
  - This is not completed
  - The current implementation works for IXBRL only

- CompanySearch
  - This class searches for companies
  - It returns an ordered list of companies
  - Each result contains the company and some brief information.
    - The results are ordered -- the top few are the most relevant -- the rest are likely to be largely unrelated.
    - I use the top n results on google (5 by default) to order the top companies. If this is problematic, tell me (Harry). This search is by nature time consuming and Google or CH will IP block if we do too many.