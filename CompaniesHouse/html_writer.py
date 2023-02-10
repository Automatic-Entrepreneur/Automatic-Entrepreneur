from typing import TextIO

from performance_summary import overall_summary


def p_write(html: TextIO, text: str, linebreak: bool = True) -> None:
	html.write(f"<p>{text}</p>\n")
	if linebreak:
		html.write("<br>\n")


def img_write(html: TextIO, img_path) -> None:
	html.write(f"<img src={img_path} alt={img_path}>\n")


def body_write(
		html: TextIO,
		sentiment: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]]
) -> None:
	p_write(html, sentiment)
	for attribute in image_paths:
		img_write(html, image_paths[attribute])
		for line in captions[attribute]:
			p_write(html, line, linebreak=False)
		html.write("<br>\n")


def html_write(
		filename: str,
		company_id: str,
		sentiment: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]]
) -> None:
	with open(filename, "w") as html:
		html.write(f"<html>\n<head>\n<title>\n{company_id} Summary</title>\n</head><body>\n")
		body_write(html, sentiment, image_paths, captions)
		html.write("</body>\n</html>")


if __name__ == "__main__":
	company_id = "03824658"
	summary = overall_summary(company_id, 2010, 2023)
	img_paths = {}
	for attribute in summary:
		img_paths[attribute] = f"{attribute}.png"
	s = "Test sentiment"
	html_write("test.html", company_id, s, img_paths, summary)
