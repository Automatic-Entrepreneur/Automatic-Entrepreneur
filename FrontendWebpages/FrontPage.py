from flask import Flask, render_template, request, redirect
from CompaniesHouse import CompanySearch
import os

app = Flask(__name__)

err_404_refreshed = False

@app.get('/')
def getMainPage():
    return render_template("searchpage.html")


@app.post('/')
def searchCompanies():
    if request.form.get('title'):
        company_search = CompanySearch()
        results = company_search.search(request.form.get('title'))
        return render_template("searchpage.html", results=results)
    else:
        return render_template("searchpage.html")


@app.get('/<company_number>')
def showData(company_number):
    global err_404_refreshed
    path_to_report = os.path.join(os.path.dirname(__file__), "reports/{}.html".format(company_number))
    if os.path.exists(path_to_report):
        return render_template(path_to_report)
    err_404_refreshed = not err_404_refreshed
    if not err_404_refreshed:
        return redirect('/')
    return render_template("error404.html", company_number=company_number)


def openFrontPage():
    app.run()


if __name__ == '__main__':
    openFrontPage()
