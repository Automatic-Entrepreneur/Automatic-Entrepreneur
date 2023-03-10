
# Everything in CompaniesHouse is wrapped in three classes.

Documentation for these is in the code

### CompanyInformation
  - This is a class which wraps API calls and extraction from accounts.

### CompanySearch
  - This class searches for companies
  - It returns a list of companies (of size n)
  - This list is sorted by date of creation
    - a reasonable heuristic as many of the newer companies are offshoots

### ScannedReportReader
  - This is primarily an internal class
  - It takes as input the byte representation of a pdf
  - And supports reading it page-by-page
