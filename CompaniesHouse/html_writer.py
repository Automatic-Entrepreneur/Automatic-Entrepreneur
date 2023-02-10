from io import TextIOWrapper
from typing import TextIO


def p_write(html: TextIO, text: str) -> None:
	html.write(f"<p>{text}\n</p>\n<br>\n")


def img_write(html: TextIO, img_path) -> None:
	html.write(f"<img src={img_path}>\n")


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
			p_write(html, line)


def html_write(
		filename: str,
		company_name: str,
		sentiment: str,
		image_paths: dict[str, str],
		captions: dict[str, list[str]]
) -> None:
	with open(filename, "w") as html:
		html.write(f"<html>\n<head>\n<title>\n{company_name} Summary</title>\n</head><body>\n")
		body_write(html, sentiment, image_paths, captions)
		html.write("</body>\n</html>")

