from typing import TextIO

from data_util import extract_data
from generate_graphs import generate_bar_graph
from performance_summary import overall_summary


def p_write(html: TextIO, text: str) -> None:
	html.write(f"<p>{text}</p>\n")


def img_write(html: TextIO, img_path: str) -> None:
	html.write(f"<img src={img_path} alt={img_path}>\n")


def body_write(
		html: TextIO,
		sentiment: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]],
) -> None:
	p_write(html, sentiment)
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
		sentiment: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]],
) -> None:
	with open(filename, "w") as html:
		html.write(
			f"<html>\n<head>\n<title>{company_id} Summary</title>\n</head>\n<body>\n"
		)
		html.write(f"<h1>{company_id} Summary</h1>")
		body_write(html, sentiment, image_paths, captions)
		html.write("</body>\n</html>")


if __name__ == "__main__":
	company_id = "03824658"
	start_year = 2010
	end_year = 2023

	sentiment = "[PLACEHOLDER SENTIMENT]"
	extracted_data = extract_data(company_id, start_year, end_year)
	summary = overall_summary(extracted_data)
	img_paths = generate_bar_graph(extracted_data, company_id, show_graph=False)
	html_write("test.html", company_id, sentiment, img_paths, summary)
