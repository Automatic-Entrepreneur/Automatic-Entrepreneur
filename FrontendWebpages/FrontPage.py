import os

from flask import Flask, render_template, request, redirect

from CompaniesHouse import CompanySearch
from html_writer import get_report

app = Flask(__name__)
err_404_refreshed = False


def generate_html(
    company_id: str, start_year: int = 2010, end_year: int = 2023
) -> None:
    report = get_report(company_id, start_year, end_year)

    with open(
        os.path.join(os.path.dirname(__file__), "templates", f"{company_id}.html"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(report)


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
    return render_template("page_not_found_404.html"), 404


def open_front_page():
    app.run()


if __name__ == "__main__":
    open_front_page()
