from fake_headers import Headers
from caption import overall_summary
from datetime import datetime
from data_util import extract_data
from generate_summary import get_text, generate_summary, answer_question, get_questions
from generate_graphs import generate_bar_graph
from news import get_news

from glassdoor_extract import *
from templates import *


def get_report(company_id, start_year=2010, end_year=2023):
	name, CH_data, GD_data, CEO_summary, QA_answers, img_paths, captions, news = get_data(company_id)
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
	out += "".join([(t.format(data=GD_data[i])+"\n") if GD_data[i] != "N/A" else "" for t, i in zip(FACTS, items)])

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
			out += T.format(img=path, caption="<p>" + ("</p>\n"+"	"*5+"<p>").join(captions[attribute]) + "</p>")

		out += GRAPHS_CLOSE

	# STOCKS

	if True:  # if we have stock data (TODO)

		if len(img_paths) != 0:
			out += DIVIDER

		out += STOCK_OPEN
		out += ""  # stock data (TODO)
		out += STOCK_CLOSE

	out += FINANCE_CLOSE

	# = WHAT PEOPLE ARE SAYING =

	out += SAYING_OPEN

	# SATISFACTION

	if True:  # if we have satisfaction data (TODO)
		out += SATISFACTION_OPEN.format(name=name)
		out += ""  # satisfaction data (TODO)
		out += SATISFACTION_CLOSE

	# NEWS

	if news != "":
		out += NEWS_OPEN.format(name=name) + news + NEWS_CLOSE

	out += SAYING_CLOSE

	# = FAQS =

	if len(QA_answers) != 0:
		out += FAQS_OPEN
		for i in QA_answers:
			out += "					<p><b>"+i["q"]+"</b> "+i["a"]+"</p>\n"
		out += FAQS_CLOSE

	# = SOCIALS =

	out += SOCIALS_OPEN

	images = [
		("Twitter", "https://upload.wikimedia.org/wikipedia/commons/4/4f/Twitter-logo.svg"),
		("LinkedIn", "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"),
		("Instagram", "https://upload.wikimedia.org/wikipedia/commons/e/e7/Instagram_logo_2016.svg"),
		("Facebook", "https://upload.wikimedia.org/wikipedia/commons/f/fb/Facebook_icon_2013.svg"),
		("YouTube", "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg")
	]

	for data, image in images:
		if GD_data[data] != "N/A":
			out += SOCIALS.format(data=GD_data[data], image=image)
	if GD_data["Website"] != "N/A":
		out += WEBSITE.format(website=GD_data["Website"])

	out += SOCIALS_CLOSE.format(time=datetime.now().strftime("%H:%M %d/%d/%Y"))

	return out


def get_data(company_id, start_year=2010, end_year=2023, torch=True):
	print("extracting data from companies house")
	CH_data = extract_data(company_id, start_year, end_year)
	name = CH_data["name"]

	print("extracting data from glassdoor")
	GD_data = glassdoor_info(company_name=CH_data["name"])

	print("generating summary")
	questions = get_questions(name)
	CEO_text, QA_text = get_text(company_id)
	CEO_summary = generate_summary(CEO_text, not torch)
	QA_answers = answer_question(QA_text, questions, not torch)

	if GD_data["Headquarters"] != "N/A":
		QA_answers.append({"q": f"Where is {name}'s headquarters?", "a": GD_data["Headquarters"]})

	print("generating graphs")
	img_paths = generate_bar_graph(
		CH_data["data"], "static/", company_id, show_graph=False
	)

	print("generating captions")
	captions = overall_summary(CH_data["data"])

	print("getting news")
	news = get_news(name)

	return name, CH_data, GD_data, CEO_summary, QA_answers, img_paths, captions, news


def glassdoor_info(company_name):
	header = Headers(
		browser="chrome",  # Generate only Chrome UA
		os="win",  # Generate only Windows platform
		headers=False  # generate misc headers
	)
	custom_user_agent = header.generate()['User-Agent']
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_experimental_option("useAutomationExtension", False)
	chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
	chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": 2})  # disables cookies
	chrome_options.add_argument(f"user-agent={custom_user_agent}")

	# This line prevents the pop-up
	chrome_options.add_argument("--headless")
	chrome_options.add_argument('--ignore-certificate-errors')
	chrome_options.add_argument('--incognito')

	driver = webdriver.Chrome(options=chrome_options)

	ret = dict()
	
	glassdoor_scrape(driver, company_name, ret)

	if ret['Ticker'] != 'N/A':
		finance_scrape(ret['Ticker'], ret)

	
	get_socials(driver, ret)
	
	return ret


if __name__ == "__main__":
	company_id = "03824658"
	start_year = 2010
	end_year = 2023

	report = get_report(company_id, start_year, end_year)

	with open(f"templates/{company_id}.html", "w") as f:
		f.write(report)
