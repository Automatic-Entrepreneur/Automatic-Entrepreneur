from flask import Flask, render_template, request
from CompaniesHouse import CompanySearch
import os

app = Flask(__name__)


@app.get('/')
def getMainPage():
    return render_template("searchpage.html")


@app.post('/')
def searchCompanies():
    company_search = CompanySearch()
    results = company_search.search(request.form.get('title'))
    return render_template("searchpage.html", results=results)


@app.get('/<company_number>')
def showData(company_number):
    path_to_report = os.path.join(os.path.dirname(__file__), "reports/{}.html".format(company_number))
    if os.path.exists(path_to_report):
        return render_template(path_to_report)
    return render_template("error404.html", company_number=company_number)


def openFrontPage():
    app.run()


if __name__ == '__main__':
    openFrontPage()
