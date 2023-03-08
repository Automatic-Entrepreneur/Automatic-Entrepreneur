"""
Provides a class which converts scanned pdfs into usable data
"""
import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
import re
from collections import defaultdict
from functools import reduce
from dateutil import parser
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"


def overlap_v(x: pd.Series, y: pd.Series) -> bool:
    """
    :param x: table entry
    :param y: potential index
    :return: True if y is a potential row index for x
    """
    return (
        (x.left > (y.left + y.width))
        and (x.top < (y.top + y.height))
        and (y.top < (x.top + x.height))
    )


def overlap_h(x: pd.Series, y: pd.Series) -> bool:
    """
    :param x: table entry
    :param y: potential index
    :return: True if y is a potential column index for x
    """
    return (
        (x.top > (y.top + y.height))
        and (x.left < (y.left + y.width))
        and (y.left < (x.left + x.width))
    )


class ScannedReportReader:
    """
    Calls pytesseract on scanned pdfs from companies house and parses them to extract company information.
    Called from CompanyInfo -- refer there for sample usage.
    To be extended in the future to support extracting textual information.
    """

    def __init__(self, pdf_bytes: bytes, year: int):
        """
        :param pdf_bytes: bytes of the pdf to process
        :param year: the year of the report
        """
        self.__images = convert_from_bytes(pdf_bytes)
        self.__year = year
        self.__num = re.compile(
            r"\d{1,3}(,\d\d\d)*(\.\d\d)?|\(\d{1,3}(,\d\d\d)*(\.\d\d)?\)"
        )
        self.__text = re.compile(r"(\S*[a-zA-Z\d]{2,}\S*){2,}")

    def __len__(self) -> int:
        return len(self.__images)

    def __numeric(self, s: str) -> bool:
        """
        True iff s is a possible entry in the table
        :param s: string to test
        :return: s is numeric
        """
        return True if self.__num.fullmatch(s) else False

    def __textual(self, s: str) -> bool:
        """
        True iff s is not an entry in the table
        :param s: string to test
        :return: s is textual
        """
        return (not self.__numeric(s)) if self.__text.fullmatch(s) else False

    def read_page_text(self, i: int) -> str:
        """
        :param i: the page to read
        :return: all text in the page i
        """
        return pytesseract.image_to_string(self.__images[i], lang="eng")

    def read_page_table(self, i: int) -> list[dict[str, any]]:
        """
        extracts tables from page i in the pdf
        :param i: the page to parse
        :return: a list of tabular information on page i
        """
        image = self.__images[i]
        attributes = []
        dirty = pytesseract.image_to_data(
            image,
            lang="eng",
            output_type=pytesseract.Output.DATAFRAME,
            config="--oem 1 --psm 11 -l eng",
        )
        page = dirty[pd.notna(dirty.text)].reset_index(drop=True).copy()
        col_to_val = defaultdict(lambda: set())
        val_to_col = defaultdict(lambda: set())
        row_to_val = defaultdict(lambda: set())
        val_to_row = defaultdict(lambda: set())

        blocks = [set()]

        for i, row in page.iterrows():
            if row.word_num == 1:
                blocks.append(set())
            blocks[row.block_num].add(i)

        for i, row in page.iterrows():
            # if numeric
            # find possible column indexes and row indexes
            if self.__numeric(row.text) and len(blocks[row.block_num]) == 1:
                for j, index in page.iterrows():
                    if self.__textual(index.text):
                        if overlap_h(row, index):
                            col_to_val[j].add(i)
                            val_to_col[i].add(j)
                        if overlap_v(row, index):
                            row_to_val[j].add(i)
                            val_to_row[i].add(j)

        drop = []

        for i in range(len(blocks)):
            # merge row keys horizontally
            # use a single key index as a leader and remove all other keys
            if (
                blocks[i]
                and not any(map(lambda x: x in col_to_val, blocks[i]))
                and not all(map(lambda x: self.__numeric(page.text[x]), blocks[i]))
            ):
                text = " ".join(
                    map(
                        lambda x: page.text[x],
                        sorted(blocks[i], key=lambda x: page.word_num[x]),
                    )
                )
                top = min(map(lambda x: page.top[x], blocks[i]))
                height = (
                    max(map(lambda x: page.top[x] + page.height[x], blocks[i])) - top
                )
                left = min(map(lambda x: page.left[x], blocks[i]))
                width = (
                    max(map(lambda x: page.left[x] + page.width[x], blocks[i])) - left
                )
                conf = reduce(lambda x, y: x * page.conf[y] / 100, blocks[i], 100)
                index = min(blocks[i])
                page.loc[index, ["text", "top", "height", "left", "width", "conf"]] = (
                    text,
                    top,
                    height,
                    left,
                    width,
                    conf,
                )
                blocks[i].remove(index)
                drop.extend(blocks[i])
                for j in blocks[i]:
                    for k in row_to_val[j]:
                        val_to_row[k].add(index)
                        val_to_row[k].remove(j)
                    row_to_val.pop(j)

        height = (
            sum(map(lambda r: r[1].height, page.iterrows())) / len(page)
            if len(page)
            else 0
        )

        page = page.drop(drop)

        for row in row_to_val:
            # if lowercase start
            # find everything which is vertically above and find a maximal set to merge with!
            if page.text[row][0].islower():
                possible = set(
                    map(
                        lambda x: x[0],
                        filter(
                            lambda x: x[0] not in row_to_val
                            and x[0] not in col_to_val
                            and overlap_h(page.loc[row, :], x[1]),
                            page.iterrows(),
                        ),
                    )
                )
                top = page.top[row]
                merge_able = {row}
                for i in sorted(possible, key=lambda x: page.top[x], reverse=True):
                    if top - page.top[i] < 3 * height:
                        merge_able.add(i)
                top = max(map(lambda x: page.top[x], merge_able))
                height = (
                    max(map(lambda x: page.top[x] + page.height[x], merge_able)) - top
                )
                left = min(map(lambda x: page.left[x], merge_able))
                width = (
                    max(map(lambda x: page.left[x] + page.width[x], merge_able)) - left
                )
                text = " ".join(
                    map(
                        lambda x: page.text[x],
                        sorted(
                            merge_able,
                            key=lambda x: page.top[x]
                            + 1
                            - (left - page.left[x]) / width,
                        ),
                    )
                )
                conf = reduce(lambda x, y: x * page.conf[y] / 100, merge_able, 100)
                page.loc[row, ["text", "top", "height", "left", "width", "conf"]] = (
                    text,
                    top,
                    height,
                    left,
                    width,
                    conf,
                )

        drop = set()

        for val, cols in val_to_col.items():
            # merge columns which are close and index the same value
            # find the sets to merge first.
            # then see about merging anything horizontally aligned!
            merge_able = set()
            top = page.top[max(cols, key=lambda x: page.top[x])]
            for col in sorted(cols, key=lambda x: page.top[x], reverse=True):
                if top - page.top[col] < 3 * height:
                    merge_able.add(col)
                    top = page.top[col]
            top = max(map(lambda x: page.top[x], merge_able))
            height = max(map(lambda x: page.top[x] + page.height[x], merge_able)) - top
            left = min(map(lambda x: page.left[x], merge_able))
            width = max(map(lambda x: page.left[x] + page.width[x], merge_able)) - left
            text = " ".join(
                map(
                    lambda x: page.text[x],
                    sorted(
                        merge_able,
                        key=lambda x: page.top[x] + 1 - (left - page.left[x]) / width,
                    ),
                )
            )
            conf = reduce(lambda x, y: x * page.conf[y] / 100, merge_able, 100)
            index = min(merge_able)
            page.loc[index, ["text", "top", "height", "left", "width", "conf"]] = (
                text,
                top,
                height,
                left,
                width,
                conf,
            )
            for col in merge_able - {index}:
                col_to_val.pop(col)
            for val_2, cols_2 in val_to_col.items():
                if merge_able & cols_2:
                    cols_2 -= merge_able
                    cols_2.add(index)
            drop |= merge_able
            drop.remove(index)

        page = page.drop(list(drop))

        val_to_col = {
            k: max(v, key=lambda x: page.top[x]) for k, v in val_to_col.items()
        }
        val_to_row = {
            k: max(v, key=lambda x: page.top[x]) for k, v in val_to_row.items()
        }

        # TODO this fails when headers aren't recognised. Could you... recognise headers the other way?
        #   some pdfs ie softwire 2011 are hardly human readable and this can't read them either
        # TODO this suffers from the header-merging issue!
        #   if headers are too close together, it can merge them

        orphaned = set(val_to_row) - set(val_to_col)
        headers = sorted(col_to_val.keys(), key=lambda x: page.left[x] + page.width[x])

        if orphaned and headers:
            # optional addition:
            # check if any of the headers are in-between the orphans
            # if so, we divide and act separately for each set of orphans
            # this only matters if there are multiple tables in a page and
            # each use different indent-levels

            # try going left -- how good is it?
            # try going right -- how good is it?
            left = min(orphaned, key=lambda x: page.left[x] + page.width[x])
            right = max(orphaned, key=lambda x: page.left[x] + page.width[x])

            valid = False

            if not (page.left[headers[-1]] < page.left[right]):
                valid = True
                for orphan in orphaned:
                    col = min(
                        filter(lambda x: page.left[x] > page.left[orphan], headers),
                        key=lambda x: page.left[x],
                    )
                    for val in col_to_val[col]:
                        if val in val_to_row and val_to_row[val] == val_to_row[orphan]:
                            valid = False
                            break
                    if not valid:
                        break
                    col_to_val[col].add(orphan)
                    val_to_col[orphan] = col
                if not valid:
                    col_to_val = {k: v - orphaned for k, v in col_to_val.items()}
                    for orphan in orphaned:
                        if orphan in val_to_col:
                            val_to_col.pop(orphan)
            if not valid and not (page.left[headers[0]] > page.left[left]):
                valid = True
                for orphan in orphaned:
                    col = max(
                        filter(lambda x: page.left[x] < page.left[orphan], headers),
                        key=lambda x: page.left[x],
                    )
                    for val in col_to_val[col]:
                        if val in val_to_row and val_to_row[val] == val_to_row[orphan]:
                            valid = False
                    if not valid:
                        break
                    col_to_val[col].add(orphan)
                    val_to_col[orphan] = col
                if not valid:
                    col_to_val = {k: v - orphaned for k, v in col_to_val.items()}
                    for orphan in orphaned:
                        if orphan in val_to_col:
                            val_to_col.pop(orphan)
            # else the file has multiple indent levels in the same page

        # a fallback to reject all dates more than 1500 days away from the query date
        threshold = 1500
        query_year = datetime(year=self.__year, month=6, day=6)
        for val in set(val_to_col) & set(val_to_row):
            # TODO make float conversion more rigorous

            match = re.match(
                r"[-+]?\d+(,\d{3})*(\.\d{2})?",
                page.text[val].replace("(", "").replace(")", ""),
            )
            if match:
                value = float(match.group().replace(",", ""))
            else:
                # unable to extract a float value
                continue
            try:
                date = parser.parse(
                    page.text[val_to_col[val]],
                    dayfirst=True,
                    fuzzy=True,
                    default=datetime(self.__year, 12, 31),
                )
                if abs((date - query_year).days) < threshold:
                    instant = date.strftime("%Y-%m-%d")
                    name = page.text[val_to_row[val]]
                else:
                    instant = name = None
            except parser.ParserError:
                try:
                    date = parser.parse(
                        page.text[val_to_row[val]],
                        dayfirst=True,
                        fuzzy=True,
                        default=datetime(self.__year, 12, 31),
                    )
                    if abs((date - query_year).days) < threshold:
                        instant = date.strftime("%Y-%m-%d")
                        name = page.text[val_to_col[val]]
                    else:
                        instant = name = None
                except parser.ParserError:
                    instant = None
                    name = None
            if name:
                attributes.append(
                    {
                        "name": name,
                        "value": value,
                        "unit": None,
                        "instant": instant,
                        "startdate": None,
                        "enddate": None,
                    }
                )
        return attributes
