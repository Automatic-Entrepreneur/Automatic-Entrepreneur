from typing import TextIO
from fake_headers import Headers
from data_util import extract_data
from generate_graphs import generate_bar_graph
from caption import overall_summary
from generate_summary import get_text, generate_summary, answer_question, get_questions
from news import get_news

from glassdoor_extract import *


def p_write(html: TextIO, text: str) -> None:
	html.write(f"<p>{text}</p>\n")


def img_write(html: TextIO, img_path: str) -> None:
	html.write(f"<img src={img_path} alt={img_path} width='500'>\n")


def facts_write(html, glassdoor_extract):
	elements = ["Industry", "Size", "Founded", "Overall Rating", "CEO"]
	facts = [glassdoor_extract[e] for e in elements]
	facts[2] = "Founded in " + facts[2]
	facts[3] = "Glassdoor rating: " + facts[3]
	facts[4] = "CEO: " + facts[4]

	html.write(
		f"""<style>	.grid-container	{{
	display: grid;
	grid-template-columns: auto auto auto auto auto;
	padding: 0px;	}}

	.grid-item	{{
	padding: 10px;
	text-align: center;
	}}	</style>"""
	)

	print(glassdoor_extract)
	html.write('<div class="grid-container">')
	for fact in facts:
		html.write(f'<div class="grid-item">{fact}</div>')
	html.write("</div>")


def write_mission_statement(html, glassdoor_extract):
	if glassdoor_extract["Mission"] != "N/A":
		p_write(html, glassdoor_extract["Mission"])


def body_write(
		html: TextIO,
		ceo_summary: str,
		qa_answers: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]],
) -> None:
	html.write(f"<h3>Report summary</h3>\n")
	p_write(html, ceo_summary + "\n\n")
	if qa_answers:
		html.write(f"<h4>FAQ</h4>\n")
		p_write(html, qa_answers)
	html.write("<br>\n")
	html.write("<br>\n")
	for attribute in image_paths:
		html.write("<div style='display:flex'>\n")
		img_write(html, image_paths[attribute])
		html.write("<div>")
		for line in captions[attribute]:
			p_write(html, line)
		html.write("</div>\n</div>\n")
		html.write("<br>\n")
		html.write("<br>\n")


def html_write(
		filename: str,
		company_name: str,
		ceo_summary: str,
		qa_answers: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]],
		glassdoor_extract: dict[str, str],
) -> None:
	with open(filename, "w", encoding="utf-8") as html:
		html.write(
			f"<!doctype html><html>\n<head>\n<meta charset='UTF-8'>\n"
			f"<title>{company_name} Summary</title>\n"
			f"<style>\n.only-print {{margin-right:250px;margin-left:250px;}}"
			f"@media print {{.only-print {{margin-right:0px;margin-left:0px;}}}}</style>\n</head>\n"
			f"<body class='only-print'>\n"
		)
		img = glassdoor_extract["Picture"]
		link = glassdoor_extract["Website"]
		html.write(
			f"""<br style='line-height:0px'>
						<h1 style='text-align:left;'>
						<img src='{img}' target='{link}' style='height:60px;position:relative;top:20px'>   {company_name} Summary
						<span style='float:right;font-size:20px'>
						<span style='color:#4285F4'>A</span>
						<span style='color:#DB4437'>u</span>
						<span style='color:#F4B400'>t</span>
						<span style='color:#0F9D58'>o</span>
						<span style='color:#DB4437'>m</span>
						<span style='color:#4285F4'>a</span>
						<span style='color:#F4B400'>t</span>
						<span style='color:#0F9D58'>i</span>
						<span style='color:#DB4437'>c</span>
						<span style='color:#F4B400'>E</span>
						<span style='color:#DB4437'>n</span>
						<span style='color:#F4B400'>t</span>
						<span style='color:#4285F4'>r</span>
						<span style='color:#F4B400'>e</span>
						<span style='color:#0F9D58'>p</span>
						<span style='color:#DB4437'>r</span>
						<span style='color:#F4B400'>e</span>
						<span style='color:#0F9D58'>n</span>
						<span style='color:#F4B400'>e</span>
						<span style='color:#DB4437'>u</span>
						<span style='color:#4285F4'>r</span>
						</span>
					</h1>
					<hr>"""
		)
		facts_write(html, glassdoor_extract)
		write_mission_statement(html, glassdoor_extract)
		body_write(html, ceo_summary, qa_answers, image_paths, captions)
		try:
			html.write(get_news(company_name) + "\n")
		except:
			pass
		social_image_links = [
			"<center>",
			*(
				f"""<a target="_blank" href={glassdoor_extract[social]}>
<img src=static/social_media_icons/{social}_icon.png alt={social} height="30" width="30">
</a>

"""
				for social in ['Twitter', 'LinkedIn', 'Instagram', 'Facebook', 'YouTube']
				if glassdoor_extract[social] != "N/A"
			),
			"</center>"]
		if social_image_links:
			html.writelines(social_image_links)
		html.write(
			"<br><br><a href='javascript:if(window.print)window.print()'>create pdf</a>\n"
		)
		html.write("</body>\n</html>")


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
	try:
		glassdoor_scrape(driver, company_name, ret)

		if ret['Ticker'] != 'N/A':
			finance_scrape(ret['Ticker'], ret)

		if ret['Website'] != 'N/A':
			get_socials(driver, ret)
	except:
		print('Please Try Again')
	return ret


if __name__ == "__main__":
	company_id = "03824658"
	start_year = 2010
	end_year = 2023

	NO_TORCH = True

	extracted_data = extract_data(company_id, start_year, end_year)

	CEO_text, QA_text = get_text(company_id)
	CEO_summary = generate_summary(CEO_text, NO_TORCH)
	QA_answers = answer_question(
		QA_text, get_questions(extracted_data["name"]), NO_TORCH
	)
	QA_answers = "<br><br>".join(
		[f"Question: {i['q']}<br>Answer: {i['a']}" for i in QA_answers]
	)

	glassdoor_extract = glassdoor_info(company_name=extracted_data["name"])
	# glassdoor_extract = {'Mission': 'N/A', 'Website': 'www.softwire.com', 'Industry': 'Software Development', 'Headquarters': 'London, United Kingdom', 'Size': '201 to 500 Employees', 'Founded': '2000', 'Recommended to Friends': '99', 'Approve of CEO': '100', 'Overall Rating': '4.8', 'CEO': 'Andrew Thomas', 'Company Type': 'Company - Private', 'Ticker': 'N/A', 'Culture & Values Rating': 'N/A', 'Diversity & Inclusion Rating': 'N/A', 'Work/Life Balance Rating': 'N/A', 'Senior Management Rating': 'N/A', 'Compensation & Benefits Rating': 'N/A', 'Career Opportunities Rating': 'N/A', 'Revenue': '$25 to $100 million (USD)', 'Price': 'N/A', 'Description': 'N/A', 'ProfitMargin': 'N/A', '52WeekHigh': 'N/A', '52WeekLow': 'N/A', '50DayMovingAverage': 'N/A', '200DayMovingAverage': 'N/A'}

	summary = overall_summary(extracted_data["data"])
	img_paths = generate_bar_graph(extracted_data["data"], "", company_id, show_graph=False)
	html_write(
		"test.html",
		extracted_data["name"],
		CEO_summary,
		QA_answers,
		img_paths,
		summary,
		glassdoor_extract,
	)
