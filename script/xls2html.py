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
    html_str = ""
    template_str = """<li>
        <div>
            <h2 style="font-family: 'Kaiti TC'"><a href="{}" target="_blank">{}</a></h2>
            <p>{}</p>
            <div>
                <span style="margin-right: 30px"><b>时间: </b>{}</span>
                <span style="margin-right: 15px"><b>一级标签: </b>{}</span>
                <span><b>二级标签: </b>{}</span>
            </div>
        </div>
    </li>
    <hr>"""
    index = 1
    for row in rows:
        if index == 1:
            index += 1
            continue
        col_list = list(row)  # type: list
        add_time = col_list[0].value
        first_tag = col_list[1].value
        second_tag = col_list[2].value
        title = col_list[3].value
        link = col_list[4].value
        ret = requests.get(link, allow_redirects=True)
        soup = BeautifulSoup(ret.text, features="lxml")
        news = soup.find(class_="newsDetail")
        if not news:
            continue
        briefs = news.find_all_next(name="p")
        brief_content = ""
        for brief in briefs:
            if len(brief.text) < 25 or "[声明]" in brief.text or "本文由新材料" in brief.text:
                continue
            else:
                brief_content += brief.text
                if len(brief_content) < 100:
                    continue
                elif len(brief_content) >= 100:
                    break

        if not brief_content:
            brief_content = title
        article_li = template_str.format(link, title, brief_content, add_time, first_tag, second_tag)
        html_str += article_li

    print(html_str)

    with open(BASE_DIR + "/file/output.text") as f:
        f.write(html_str)

    print("Success!!!")
