import os

from flask import Flask, render_template, request, redirect

from CompaniesHouse import CompanySearch
from data_util import extract_data
from generate_graphs import generate_bar_graph
from generate_summary import get_text, generate_summary, answer_question, questions
from html_writer import html_write, glassdoor_info
from caption import overall_summary


def generate_html(
        company_id: str, start_year: int = 2010, end_year: int = 2023
) -> None:
    ceo_text, qa_text = get_text(company_id)
    try:
        ceo_summary = generate_summary(ceo_text, False)
        qa_answers = answer_question(qa_text, questions, False)
    except:
        ceo_summary = generate_summary(ceo_text, True)
        qa_answers = answer_question(qa_text, questions, True)

    qa_answers = "<br><br>".join(
        [f"Question: {i['q']}<br>Answer: {i['a']}" for i in qa_answers]
    )

    # qa_answers = ""

    extracted_data = extract_data(company_id, start_year, end_year)
    glassdoor_extract = glassdoor_info(extracted_data["name"])

    summary = overall_summary(extracted_data["data"])
    img_paths = generate_bar_graph(
        extracted_data["data"], "static/", company_id, show_graph=False
    )
    html_write(
        f"templates/{company_id}.html",
        extracted_data["name"],
        ceo_summary,
        qa_answers,
        img_paths,
        summary,
        glassdoor_extract,
    )


app = Flask(__name__)

err_404_refreshed = False


@app.get("/")
def get_main_page():
    return render_template("searchpage.html")


@app.post("/")
def search_companies():
    if request.form.get("title"):
        company_search = CompanySearch()
        results = company_search.search(request.form.get("title"))
        return render_template("searchpage.html", results=results)
    else:
        return render_template("searchpage.html")


@app.route("/report", methods=["GET", "POST"])
def generate_report():
    if request.method == "POST":
        company_search = CompanySearch()
        results = company_search.search(request.form["companyName"])
        company_id = results[0]["company_number"]
        path_to_report = os.path.join(
            os.path.dirname(__file__), f"templates/{company_id}.html"
        )
        if not os.path.exists(path_to_report):
            generate_html(company_id)
        return company_id
        # return redirect(url_for("showData", company_number=company_id), code=302)


@app.get("/<company_number>")
def show_data(company_number):
    global err_404_refreshed
    path_to_report = os.path.join(
        os.path.dirname(__file__), "templates/{}.html".format(company_number)
    )
    if os.path.exists(path_to_report):
        return render_template(f"{company_number}.html")
    err_404_refreshed = not err_404_refreshed
    if not err_404_refreshed:
        return redirect("/")
    return render_template("company_not_found_404.html", company_number=company_number)


@app.errorhandler(404)
def page_not_found(_):
    global err_404_refreshed
    err_404_refreshed = not err_404_refreshed
    if not err_404_refreshed:
        return redirect("/")
    return render_template('page_not_found_404.html'), 404


def open_front_page():
    app.run()


if __name__ == "__main__":
    open_front_page()
