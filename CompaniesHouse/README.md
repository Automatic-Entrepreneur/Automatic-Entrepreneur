
# Everything in CompaniesHouse is wrapped in two classes.

Documentation for these is in the code

- CompanyInformation
  - This is a class which wraps API calls and extraction from accounts.
  - This is not completed
  - The current implementation works for IXBRL only

- CompanySearch
  - This class searches for companies
  - It returns a list of companies (of size n)
  - This list is sorted by date of creation
    - a reasonable heuristic as many of the newer companies are offshoots