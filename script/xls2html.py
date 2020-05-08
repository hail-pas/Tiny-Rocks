import os

import requests
from openpyxl import load_workbook
from openpyxl.cell import Cell
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    wb = load_workbook(filename=BASE_DIR + "/file/a.xlsx")
    ws = wb.active
    rows = ws.rows
    for row in rows:
        col_list = list(row)  # type: list
        add_time = col_list[0]  # type: Cell
        first_tag = col_list[0]  # type: Cell
        second_tag = col_list[0]  # type: Cell
        title = col_list[0]  # type: Cell
        link = col_list[0]  # type: Cell
        ret = requests.get(link, allow_redirects=True)
        soup = BeautifulSoup(ret.text, features="lxml")
        news = soup.find(class_="newsDetail")
        if not news:
            continue
        brief = news.find(name="p")
        if brief:
            brief.text
