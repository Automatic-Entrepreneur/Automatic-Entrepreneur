import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
import re
from collections import defaultdict
from functools import reduce
from dateutil import parser
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"


class ScannedReportReader:
    """
    Calls pytesseract on scanned pdfs from companies house and parses them to extract company information.
    Called from CompanyInfo -- refer there for sample usage.
    To be extended in the future to support extracting textual information.
    """
    def __init__(self, pdf_bytes, year):
        """
        :param pdf_bytes: bytes of the pdf -- requests.get().content
        :param year: the year of the report
        :type year: int
        """
        self.__images = convert_from_bytes(pdf_bytes)
        self.__year = year
        self.__num = re.compile(r"\d{1,3}(,\d\d\d)*(\.\d\d)?|\(\d{1,3}(,\d\d\d)*(\.\d\d)?\)")
        self.__text = re.compile(r"(\S*[a-zA-Z\d]{2,}\S*){2,}")

    def __len__(self):
        return len(self.__images)

    def __numeric(self, s):
        """
        True iff s is a possible entry in the table
        :param s: string to test
        :type s: str
        :return: s is numeric
        :rtype: bool
        """
        return True if self.__num.fullmatch(s) else False

    def __textual(self, s):
        """
        True iff s is not an entry in the table
        :param s: string to test
        :type s: str
        :return: s is textual
        :rtype: bool
        """
        return (not self.__numeric(s)) if self.__text.fullmatch(s) else False

    def __overlap_h(self, x, y):
        """
        :param x: table entry
        :type x: pd.Series
        :param y: potential index
        :type y: pd.Series
        :return: True if y is a potential column index for x
        :rtype: bool
        """
        return (x.top > (y.top + y.height)) and (x.left < (y.left + y.width)) and (y.left < (x.left + x.width))

    def __overlap_v(self, x, y):
        """
        :param x: table entry
        :type x: pd.Series
        :param y: potential index
        :type y: pd.Series
        :return: True if y is a potential row index for x
        :rtype: bool
        """
        return (x.left > (y.left + y.width)) and (x.top < (y.top + y.height)) and (y.top < (x.top + x.height))

    def readPage(self, i):
        """
        extracts tables from page i in the pdf
        :param i: the page to parse
        :type i: int
        :return:
        """
        image = self.__images[i]
        attributes = []
        dirty = pytesseract.image_to_data(image, lang='eng', output_type=pytesseract.Output.DATAFRAME, config='--oem 1 --psm 11 -l eng')
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
                for j, indx in page.iterrows():
                    if self.__textual(indx.text):
                        if self.__overlap_h(row, indx):
                            col_to_val[j].add(i)
                            val_to_col[i].add(j)
                        if self.__overlap_v(row, indx):
                            row_to_val[j].add(i)
                            val_to_row[i].add(j)

        drop = []

        for i in range(len(blocks)):
            # merge row keys horizontally
            # use a single key indx as a leader and remove all other keys
            if blocks[i] and not any(map(lambda x: x in col_to_val, blocks[i])) and not all(map(lambda x: self.__numeric(page.text[x]), blocks[i])):
                text = " ".join(map(lambda x: page.text[x], sorted(blocks[i], key=lambda x: page.word_num[x])))
                top = min(map(lambda x: page.top[x], blocks[i]))
                height = max(map(lambda x: page.top[x] + page.height[x], blocks[i])) - top
                left = min(map(lambda x: page.left[x], blocks[i]))
                width = max(map(lambda x: page.left[x] + page.width[x], blocks[i])) - left
                conf = reduce(lambda x, y: x * page.conf[y] / 100, blocks[i], 100)
                indx = min(blocks[i])
                page.loc[indx, ['text', 'top', 'height', 'left', 'width', 'conf']] = text, top, height, left, width, conf
                blocks[i].remove(indx)
                drop.extend(blocks[i])
                for x in blocks[i]:
                    for y in row_to_val[x]:
                        val_to_row[y].add(indx)
                        val_to_row[y].remove(x)
                    row_to_val.pop(x)

        height = sum(map(lambda row: row[1].height, page.iterrows())) / len(page) if len(page) else 0

        page = page.drop(drop)

        for row in row_to_val:
            # if lowercase start
            # find everything which is vertically above and find a maximal set to merge with!
            if page.text[row][0].islower():
                possible = set(map(lambda x: x[0], filter(lambda x: x[0] not in row_to_val and x[0] not in col_to_val and self.__overlap_h(page.loc[row, :], x[1]), page.iterrows())))
                top = page.top[row]
                mergeable = {row}
                for i in sorted(possible, key=lambda x: page.top[x], reverse=True):
                    if top - page.top[i] < 3 * height:
                        mergeable.add(i)
                top = max(map(lambda x: page.top[x], mergeable))
                height = max(map(lambda x: page.top[x] + page.height[x], mergeable)) - top
                left = min(map(lambda x: page.left[x], mergeable))
                width = max(map(lambda x: page.left[x] + page.width[x], mergeable)) - left
                text = " ".join(map(lambda x: page.text[x], sorted(mergeable, key=lambda x: page.top[x] + 1 - (left - page.left[x]) / width)))
                conf = reduce(lambda x, y: x * page.conf[y] / 100, mergeable, 100)
                page.loc[row, ['text', 'top', 'height', 'left', 'width', 'conf']] = text, top, height, left, width, conf

        drop = set()

        for val, cols in val_to_col.items():
            # merge columns which are close and index the same value
            # find the sets to merge first.
            # then see about merging anything horizontally aligned!
            mergeable = set()
            top = page.top[max(cols, key=lambda x: page.top[x])]
            for col in sorted(cols, key=lambda x: page.top[x], reverse=True):
                if top - page.top[col] < 3 * height:
                    mergeable.add(col)
                    top = page.top[col]
            top = max(map(lambda x: page.top[x], mergeable))
            height = max(map(lambda x: page.top[x] + page.height[x], mergeable)) - top
            left = min(map(lambda x: page.left[x], mergeable))
            width = max(map(lambda x: page.left[x] + page.width[x], mergeable)) - left
            text = " ".join(map(lambda x: page.text[x], sorted(mergeable, key=lambda x: page.top[x] + 1 - (left - page.left[x]) / width)))
            conf = reduce(lambda x, y: x * page.conf[y] / 100, mergeable, 100)
            indx = min(mergeable)
            page.loc[indx, ['text', 'top', 'height', 'left', 'width', 'conf']] = text, top, height, left, width, conf
            for col in mergeable - {indx}:
                col_to_val.pop(col)
            for val, cols in val_to_col.items():
                if mergeable & cols:
                    cols -= mergeable
                    cols.add(indx)
            drop |= mergeable
            drop.remove(indx)

        page = page.drop(list(drop))

        val_to_col = {k: max(v, key=lambda x: page.top[x]) for k, v in val_to_col.items()}
        val_to_row = {k: max(v, key=lambda x: page.top[x]) for k, v in val_to_row.items()}

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
                    col = min(filter(lambda x: page.left[x] > page.left[orphan], headers), key=lambda x: page.left[x])
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
                    col = max(filter(lambda x: page.left[x] < page.left[orphan], headers), key=lambda x: page.left[x])
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
        for val in set(val_to_col) & set(val_to_row):
            # TODO make this float conversion more rigorous
            match = re.match(r'[-+]?\d+(,\d{3})*(\.\d{2})?', page.text[val].replace("(", "").replace(")", ""))
            if match:
                value = float(match.group().replace(",", ""))
            else:
                # unable to extract a float value
                continue
            try:
                instant = parser.parse(page.text[val_to_col[val]], dayfirst=True, fuzzy=True, default=datetime(self.__year, 12, 31)).strftime('%Y-%m-%d')
                name = page.text[val_to_row[val]]
            except:
                try:
                    instant = parser.parse(page.text[val_to_row[val]], dayfirst=True, fuzzy=True, default=datetime(self.__year, 12, 31)).strftime('%Y-%m-%d')
                    name = page.text[val_to_col[val]]
                except:
                    instant = None
                    name = None
            if name:
                attributes.append(
                    {
                        'name': name,
                        'value': value,
                        'unit': None,
                        'instant': instant,
                        'startdate': None,
                        'enddate': None
                    }
                )
        return attributes
