from typing import TextIO

from data_util import extract_data
from generate_graphs import generate_bar_graph
from performance_summary import overall_summary
from generate_summary import get_text, generate_summary, answer_question, questions


def p_write(html: TextIO, text: str) -> None:
	html.write(f"<p>{text}</p>\n")


def img_write(html: TextIO, img_path: str) -> None:
	html.write(f"<img src={img_path} alt={img_path} width='500'>\n")


def body_write(
		html: TextIO,
		CEO_summary: str,
		QA_answers: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]],
) -> None:
	html.write(f"<h3>Report summary</h3>\n")
	p_write(html, CEO_summary+"\n\n")
	html.write(f"<h4>FAQ</h4>\n")
	p_write(html, QA_answers)
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
		CEO_summary: str,
		QA_answers: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]],
) -> None:
	with open(filename, "w") as html:
		html.write(
			f"<html>\n<head>\n<title>{company_name} Summary</title>\n</head>\n<body style='margin-right:250px;margin-left:250px;'>\n"
		)
		html.write(f'''<br style='line-height:0px'><h1 style='text-align:left;'>
						{company_name} Summary
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
					<hr>''')
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

	summary = overall_summary(extracted_data["data"])
	img_paths = generate_bar_graph(extracted_data["data"], company_id, show_graph=False)
	html_write("test.html", extracted_data["name"], CEO_summary, QA_answers, img_paths, summary)
