from flask import Flask, render_template, request
from CompaniesHouse import CompanySearch

app = Flask(__name__)


@app.get('/')
def indices():
    return render_template("index.html")


@app.post('/')
def search():
    srch = CompanySearch()
    results = srch.search(request.form.get('title'))
    return render_template("index.html", results=results)


def openFrontPage():
    app.run()
