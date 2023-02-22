from flask import Flask, render_template, request, redirect, url_for
from CompaniesHouse import CompanySearch
import os

from data_util import extract_data
from generate_graphs import generate_bar_graph
from generate_summary import get_text, generate_summary, answer_question, questions
from html_writer import html_write
from performance_summary import overall_summary


def generateHTML(company_id: str, start_year: int = 2010, end_year: int = 2023) -> None:
    '''
    CEO_text, QA_text = get_text(company_id)
    CEO_summary = generate_summary(CEO_text)
    QA_answers = answer_question(QA_text, questions)
    QA_answers = "<br><br>".join([f"Question: {i['q']}<br>Answer: {i['a']}" for i in QA_answers])
    '''

    NO_TORCH = True
    CEO_text, QA_text = get_text(company_id)
    CEO_summary = generate_summary(CEO_text, NO_TORCH)
    QA_answers = answer_question(QA_text, questions, NO_TORCH)
    QA_answers = "<br><br>".join([f"Question: {i['q']}<br>Answer: {i['a']}" for i in QA_answers])

    extracted_data = extract_data(company_id, start_year, end_year)

    summary = overall_summary(extracted_data["data"])
    img_paths = generate_bar_graph(extracted_data["data"], "static/", company_id, show_graph=False)
    html_write(f"templates/{company_id}.html", extracted_data["name"], CEO_summary, QA_answers, img_paths, summary)


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


@app.route('/report', methods=['GET', 'POST'])
def generateReport():
    if request.method == "POST":
        company_search = CompanySearch()
        results = company_search.search(request.form["companyName"])
        company_id = results[0]["company_number"]
        generateHTML(company_id)
        # print(company_id)
        return company_id
        # return redirect(url_for("showData", company_number=company_id), code=302)


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
