from typing import TextIO

from data_util import extract_data
from generate_graphs import generate_bar_graph
from performance_summary import overall_summary
from generate_summary import get_text, generate_summary, answer_question, questions


def p_write(html: TextIO, text: str) -> None:
	html.write(f"<p>{text}</p>\n")


def img_write(html: TextIO, img_path: str) -> None:
	html.write(f"<img src={img_path} alt={img_path}>\n")


def body_write(
		html: TextIO,
		CEO_summary: str,
		QA_answers: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]],
) -> None:
	html.write(f"<h4>Report summary</h4>\n")
	p_write(html, CEO_summary+"\n\n")
	html.write(f"<h4>FAQ</h4>\n")
	p_write(html, QA_answers)
	html.write("<br>\n")
	html.write("<br>\n")
	for attribute in image_paths:
		img_write(html, image_paths[attribute])
		for line in captions[attribute]:
			p_write(html, line)
		html.write("<br>\n")
		html.write("<br>\n")


def html_write(
		filename: str,
		company_id: str,
		CEO_summary: str,
		QA_answers: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]],
) -> None:
	with open(filename, "w") as html:
		html.write(
			f"<html>\n<head>\n<title>\n{company_id} Summary</title>\n</head><body>\n"
		)
		html.write(f"<h1>{company_id} Summary</h1>")
		body_write(html, CEO_summary, QA_answers, image_paths, captions)
		html.write("</body>\n</html>")


if __name__ == "__main__":
	company_id = "03824658"
	start_year = 2010
	end_year = 2023

	NO_TORCH = True

	CEO_text, QA_text = get_text(company_id)
	CEO_summary = generate_summary(CEO_text, NO_TORCH)
	QA_answers = answer_question(QA_text, questions, NO_TORCH)
	QA_answers = "<br><br>".join([f"Question: {i['q']}<br>Answer: {i['a']}" for i in QA_answers])

	extracted_data = extract_data(company_id, start_year, end_year)
	summary = overall_summary(extracted_data)
	img_paths = generate_bar_graph(extracted_data, company_id, show_graph=False)
	html_write("out/test.html", company_id, CEO_summary, QA_answers, img_paths, summary)
