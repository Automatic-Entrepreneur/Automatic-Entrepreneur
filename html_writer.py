from datetime import datetime

from fake_headers import Headers
from selenium import webdriver

from caption import overall_summary
from data_util import extract_data
from generate_financetable import generate_table
from generate_graphs import generate_bar_graph
from generate_summary import get_text, generate_summary, answer_question, get_questions
from glassdoor_extract import *
from news import get_news
from templates import *


def get_report(company_id, start_year=2010, end_year=2023, torch=True, front_page=True):
    (
        name,
        CH_data,
        GD_data,
        CEO_summary,
        QA_answers,
        img_paths,
        captions,
        news,
    ) = get_data(company_id, start_year, end_year, torch=torch, front_page=front_page)

    out = ""
    print(GD_data)

    # == TITLE ==
    out += HEAD.format(name=name, website=GD_data.get("Website", ""))
    if "Picture" in GD_data:
        out += TITLE_P.format(name=name, logo=GD_data["Picture"])
    else:
        out += TITLE_N.format(name=name)
    out += LOGO

    items = ["Industry", "Size", "Founded", "Overall Rating", "CEO"]
    out += "".join(
        [
            (t.format(data=GD_data[i]) + "\n") if GD_data[i] != "N/A" else ""
            for t, i in zip(FACTS, items)
        ]
    )

    # == BODY ==

    # = FACTS =
    out += MAIN

    # = MISSION =
    if GD_data["Mission"] != "N/A":
        out += MISSION.format(mission=GD_data["Mission"])
    # = REPORT =
    if CEO_summary != "":
        out += REPORT.format(report=CEO_summary, id=company_id)
    # = FINANCE =
    out += FINANCE_OPEN

    # GRAPHS
    if len(img_paths) != 0:
        out += GRAPHS_OPEN
        for i, (attribute, path) in enumerate(img_paths.items()):
            if i % 2 == 0:
                T = IMAGE_L
            else:
                T = IMAGE_R
            out += T.format(
                img=path,
                caption="<p>"
                + ("</p>\n" + "	" * 5 + "<p>").join(captions[attribute])
                + "</p>",
            )
        out += GRAPHS_CLOSE

    # STOCKS
    if GD_data["Ticker"] != "N/A":  # Checks if attributes found in GD_data
        if len(img_paths) != 0:
            out += DIVIDER
        out += STOCK_OPEN
        try:  # if all stock info available
            out += STOCK.format(
                name=GD_data["Name"],
                symbol=GD_data["Symbol"],
                exchange=GD_data["Exchange"],
                currency=GD_data["Currency"],
                price=GD_data["Price"],
                tradevol=GD_data["Trade Volume (Day)"],
                change=GD_data["Change Percentage (Day)"],
                _52hi=GD_data["52WeekHigh"],
                _52lo=GD_data["52WeekLow"],
                _50ave=GD_data["50DayMovingAverage"],
                _200ave=GD_data["200DayMovingAverage"],
                marketcap=GD_data["MarketCapitalization"],
                ebitda=GD_data["EBITDA"],
                peratio=GD_data["PERatio"],
                pegratio=GD_data["PEGRatio"],
                bookval=GD_data["BookValue"],
                profitmargin=GD_data["ProfitMargin"],
            )
        except:
            try:  # if only general (GLOBAL_QUOTE) available
                out += STOCK_ONLY.format(
                    symbol=GD_data["Symbol"],
                    hi=GD_data["High (Day)"],
                    lo=GD_data["Low (Day)"],
                    price=GD_data["Price"],
                    tradevol=GD_data["Trade Volume (Day)"],
                    change=GD_data["Change Percentage (Day)"],
                )
            except:  # if ticker exists but Alpha Vantage does not have any info
                pass
        out += STOCK_CLOSE
        if "Balance Sheet" in GD_data:
            out += TABLE.format(table=generate_table(GD_data))
    out += FINANCE_CLOSE

    # = WHAT PEOPLE ARE SAYING =
    out += SAYING_OPEN

    # SATISFACTION
    employee_sat_attributes = {}
    if "Overall Rating" in GD_data.keys():
        if GD_data["Overall Rating"] != "N/A":
            employee_sat_attributes["overall_rating"] = float(GD_data["Overall Rating"])
    if "Recommended to Friends" in GD_data.keys():
        if GD_data["Recommended to Friends"] != "N/A":
            employee_sat_attributes["recommended_to_friend"] = float(
                GD_data["Recommended to Friends"]
            )
    if "Approve of CEO" in GD_data.keys():
        if GD_data["Approve of CEO"] != "N/A":
            employee_sat_attributes["approve_of_CEO"] = float(GD_data["Approve of CEO"])

    if len(employee_sat_attributes) >= 1:
        out += SATISFACTION_OPEN.format(name=name)
        # Use the GD data to get generate a pie-chart of the satisfaction of the company
        # satisfaction data
        """employee_sat_attributes = {'overall_rating': float(GD_data['Overall Rating']),
								   'recommended_to_friend': float(GD_data['Recommended to Friends']),
								   'approve_of_CEO': float(GD_data['Approve of CEO'])}"""
        out += generate_pie_charts(
            employee_sat_attributes, len(employee_sat_attributes)
        )
        out += SATISFACTION_CLOSE

    # NEWS
    if news != "":
        out += NEWS_OPEN.format(name=name) + news + NEWS_CLOSE
    out += SAYING_CLOSE

    # = FAQS =
    if len(QA_answers) != 0:
        out += FAQS_OPEN
        for i in QA_answers:
            out += "					<p><b>" + i["q"] + "</b> " + i["a"] + "</p>\n"
        out += FAQS_CLOSE
    # = SOCIALS =
    out += SOCIALS_OPEN
    images = [
        (
            "Twitter",
            "https://upload.wikimedia.org/wikipedia/commons/4/4f/Twitter-logo.svg",
        ),
        (
            "LinkedIn",
            "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png",
        ),
        (
            "Instagram",
            "https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg",
        ),
        (
            "Facebook",
            "https://upload.wikimedia.org/wikipedia/commons/f/fb/Facebook_icon_2013.svg",
        ),
        (
            "YouTube",
            "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
        ),
    ]
    for data, image in images:
        if data in GD_data.keys():
            if GD_data[data] != "N/A":
                out += SOCIALS.format(data=GD_data[data], image=image)
    if GD_data["Website"] != "N/A":
        out += WEBSITE.format(website=GD_data["Website"])
    out += SOCIALS_CLOSE.format(time=datetime.now().strftime("%H:%M %d/%d/%Y"))
    return out


def get_data(company_id, start_year=2010, end_year=2023, torch=True, front_page=True):
    print("extracting data from companies house")
    CH_data = extract_data(company_id, start_year, end_year)
    name = CH_data["name"]

    print("extracting data from glassdoor")
    GD_data = glassdoor_info(company_id=company_id, company_name=CH_data["name"])
    """
	GD_data = {'Company': 'Softwire',
	           'Picture': 'https://media.glassdoor.com/sqls/251160/softwire-squarelogo-1506517702277.png',
	           'Mission': 'N/A',
	           'Description': 'Softwire is a privately owned software development company based in London, UK. We are specialists in the delivery of software consultancy and bespoke, custom-built software solutions.\r\n\r\nSoftwire focus on providing an exceptional level of service to a manageable number of',
	           'Website': 'www.softwire.com', 'Industry': 'Software Development',
	           'Headquarters': 'London, United Kingdom', 'Size': '201 to 500 Employees', 'Recommended to Friends': '99',
	           'Approve of CEO': '100', 'Overall Rating': '4.8', 'Diversity & Inclusion Rating': '4.6',
	           'CEO': 'Andrew Thomas', 'Company Type': 'Company - Private', 'Ticker': 'N/A',
	           'Culture & Values Rating': 'N/A', 'Work/Life Balance Rating': 'N/A', 'Senior Management Rating': 'N/A',
	           'Compensation & Benefits Rating': 'N/A', 'Career Opportunities Rating': 'N/A', 'Founded': '2000',
	           'Revenue': '$25 to $100 million (USD)', 'Twitter': 'https://twitter.com/softwireuk',
	           'LinkedIn': 'https://www.linkedin.com/company/softwire/',
	           'Instagram': 'https://www.instagram.com/softwireuk/', 'Facebook': 'https://www.facebook.com/softwire',
	           'YouTube': 'https://www.youtube.com/channel/UCVvQUh9ByC1dQB7x7mudReQ'}
	"""
    print("generating summary")
    questions = get_questions(name)
    CEO_text, QA_text = get_text(company_id)
    CEO_summary = generate_summary(company_id, CEO_text, not torch)
    QA_answers = answer_question(QA_text, questions, not torch)

    if GD_data["Headquarters"] != "N/A":
        QA_answers.append(
            {"q": f"Where is {name}'s headquarters?", "a": GD_data["Headquarters"]}
        )

    img_dir = "static/img/"
    if not front_page:
        img_dir = "FrontendWebpages/" + img_dir
    img_paths = generate_bar_graph(
        CH_data["data"], img_dir, company_id, show_graph=False
    )

    print("generating captions")
    captions = overall_summary(CH_data["data"])

    print("getting news")
    if torch:
        news = get_news(GD_data["Company"])
    else:
        news = ""

    return name, CH_data, GD_data, CEO_summary, QA_answers, img_paths, captions, news


def glassdoor_info(company_id, company_name):
    ret = dict()

    """
	root = os.path.dirname(__file__)
	base_path = os.path.join(root, f"glassdoor/cache/{company_id}")
	i = 0
	path = base_path + f"_{i}.pkl"
	while os.path.exists(path):
		attribute, content = pkl.load(open(path, "rb"))
		ret[attribute] = content
		i += 1
		path = base_path + f"_{i}.pkl"
	if i > 0:
		return ret
	"""

    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate only Windows platform
        headers=False,  # generate misc headers
    )
    custom_user_agent = header.generate()["User-Agent"]
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.cookies": 2}
    )  # disables cookies
    chrome_options.add_argument(f"user-agent={custom_user_agent}")

    # This line prevents the pop-up
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    glassdoor_scrape(driver, company_name, ret)

    if ret["Ticker"] != "N/A":
        finance_scrape(ret["Ticker"], ret)
    get_socials(driver, ret)

    """
	i = 0
	path = base_path + f"_{i}.pkl"
	for attribute, content in ret.items():
		pkl.dump((attribute, content), open(path, "wb"))
		i += 1
		path = base_path + f"_{i}.pkl"
	"""

    return ret


def generate_pie_chart_html(name, degrees):
    return f"""<style>
        .{name}_piechart {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin: auto;
            background-image: conic-gradient( 
                orange {degrees}deg, 
                lightblue 0);
        }}
    </style>
"""


def generate_pie_charts(attributes, num_attributes):
    autos = " ".join(["auto" for i in range(num_attributes)])
    return_string = f"""
	<style>    	.grid-container-2	{{
			display: grid;
			grid-template-columns: {autos};
			padding: 0px;
		}}
		.grid-item-2	{{
			padding: 10px;
			text-align: center;
		}}
		</style>
		"""
    return_string += (
        f"""<div class="grid-container-2" style="position:relative;top:-5px">"""
    )
    for name in attributes.keys():
        if name == "overall_rating":
            return_string += generate_pie_chart_html(
                name, int(attributes[name] * 360 / 5)
            )
            return_string += f"""<div class="grid-item-2">
				<div class="{name}_piechart"></div>
				<div><strong>Glassdoor rating {attributes[name]} stars</strong></div>
			</div>"""
        elif name == "recommended_to_friend":
            return_string += generate_pie_chart_html(
                name, int(attributes[name] * 360 / 100)
            )
            return_string += f"""<div class="grid-item-2">
				<div class="{name}_piechart"></div>
				<div><strong>{int(attributes[name])}% Recommended to a friend</strong></div>
			</div>"""
        elif name == "Approve of CEO":
            return_string += generate_pie_chart_html(
                name, int(attributes[name] * 360 / 100)
            )
            return_string += f"""<div class="grid-item-2">
				<div class="{name}_piechart"></div>
				<div><strong>{int(attributes[name])}% Approve of the CEO</strong></div>
			</div>"""

    return_string += """</div>"""
    return return_string


if __name__ == "__main__":
    company_id = "03824658"
    start_year = 2010
    end_year = 2023

    report = get_report(company_id, start_year, end_year, False, front_page=False)

    with open(f"{company_id}.html", "w") as f:
        f.write(report)
