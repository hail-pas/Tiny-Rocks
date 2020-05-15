import os
from datetime import datetime

import requests
from openpyxl import load_workbook
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_html():
    file_name = input("输入文档路径(包含文件名), 如果要退出请输入q：")
    if file_name == "q":
        exit()
    if not (file_name.endswith("xls") or file_name.endswith("xlsx")):
        print("文件名错误或不存在！")
        return create_html()
    prefix = str(datetime.now()).split(".")[0].replace(" ", "_")
    output_file = file_name.split(".")[0] + f"-{prefix}.html"
    wb = load_workbook(filename=file_name)
    ws = wb.active
    rows = ws.rows
    html_str = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>新闻浏览-新材料在线</title>
        <style>
            h2 a {
                text-decoration: none
            }

            div a {
                text-decoration: none
            }

            a:hover {
                text-decoration: underline
            }

            h2 a:active {
                color: black;
            }

            h2 a:visited {
                color: grey
            }

            h2 {
                font-family: STKaiti, Kaiti TC, KaiTi, KaiTi_GB2312;
            !important;
            }
        </style>
    </head>
    <body style="margin-left: 9%; width: 80%">

    <h1 style="font-family: 'STKaiti, Kaiti TC, KaiTi, KaiTi_GB2312'; font-size: 50px; margin-bottom: 30px;margin-left: 45%; margin-right: -100px">
        <b>行业新闻</b>
    </h1>

    <div style="margin-left: 3%; margin-bottom: 40px; font-size: x-large"><span style="color: green; font-size: x-large">标签分类</span>："""

    tail_str = """</ul>
    <div id="barcon" name="barcon"></div>
    <script>
        function goPage(pno, psize, tagName) {

            let aItem = document.getElementsByClassName("tag");
            for (let index = 0; index < aItem.length; index++) {
                if (aItem[index].id === tagName) {
                    aItem[index].style.backgroundColor = "cornflowerblue";
                } else {
                    aItem[index].style.backgroundColor = "white";
                }
            }

            let items = document.getElementsByTagName("ul");
            let hrs = document.getElementsByTagName("hr");
            let itemss = items[0].getElementsByTagName("li");
            let filteredLiItem = [];
            let filteredHrItem = []
            let f_index = 0;
            for (let index = 0; index < itemss.length; index++) {
                itemss[index].style.display = 'none';
                hrs[index].style.display = 'none';
                let tagContent = itemss[index].getElementsByTagName("span")[1].textContent;
                if (tagContent.search(tagName) !== -1) {
                    filteredLiItem[f_index] = itemss[index];
                    filteredHrItem[f_index] = hrs[index];
                    f_index += 1;
                }
            }
            var all_num = itemss.length;
            var num = filteredLiItem.length;
            var totalPage = 0;//总页数
            var pageSize = psize;//每页显示行数
            //总共分几页
            if (num / pageSize > parseInt(num / pageSize)) {
                totalPage = parseInt(num / pageSize) + 1;
            } else {
                totalPage = parseInt(num / pageSize);
            }
            var currentPage = pno;//当前页数
            var startRow = (currentPage - 1) * pageSize + 1;//开始显示的行 31
            var endRow = currentPage * pageSize;//结束显示的行  40
            endRow = (endRow > num) ? num : endRow;  //40
            //遍历显示数据实现分页
            for (var i = 1; i < (num + 1); i++) {
                var irow = filteredLiItem[i - 1];
                var irow2 = filteredHrItem[i - 1];
                if (i >= startRow && i <= endRow) {
                    irow.style.display = "block";
                    irow2.style.display = "block";
                } else {
                    irow.style.display = "none";
                    irow2.style.display = "none";
                }
            }

            var tempStr = `<div style="margin-left: 50%; margin-top: 20px; margin-right:-174px; margin-bottom: 40px; font-size: large">` + "总计 " + all_num + " 条； " + "标签 " + `<span style="color: green; font-style: italic" >` + tagName + "</span>" + " 下 " + num + " 条  分" + totalPage + "页 当前 第 " + currentPage + " 页";
            if (currentPage > 1) {
                tempStr += `<a href="#" onClick="goPage(1,${psize} ,'${tagName}')"> 首页 </a>`;
                tempStr += `<a href="#" onClick="goPage(${currentPage - 1},${psize} ,'${tagName}')"> <上一页 </a>`;
            } else {
                tempStr += " 首页 ";
                tempStr += " <上一页 ";
            }
            if (currentPage < totalPage) {
                tempStr += `<a href="#" onClick="goPage(${currentPage + 1},${psize} ,'${tagName}')"> 下一页> </a>`;
                tempStr += `<a href="#" onClick="goPage(${totalPage},${psize} ,'${tagName}')"> 尾页 </a>`;
            } else {
                tempStr += " 下一页> ";
                tempStr += " 尾页 ";
            }
            tempStr += "</div>";
            document.getElementById("barcon").innerHTML = tempStr;
        }

        function goPageAll(pno, psize, tagName) {
            let aItem = document.getElementsByClassName("tag");
            for (let index = 0; index < aItem.length; index++) {
                if (aItem[index].id === tagName) {
                    aItem[index].style.backgroundColor = "cornflowerblue";
                } else {
                    aItem[index].style.backgroundColor = "white";
                }
            }


            let items = document.getElementsByTagName("ul");
            let hrs = document.getElementsByTagName("hr");
            let itemss = items[0].getElementsByTagName("li");
            for (let index = 0; index < itemss.length; index++) {
                itemss[index].style.display = 'none';
                hrs[index].style.display = 'none';
            }
            var all_num = itemss.length;
            var num = itemss.length;
            var totalPage = 0;//总页数
            var pageSize = psize;//每页显示行数
            //总共分几页
            if (num / pageSize > parseInt(num / pageSize)) {
                totalPage = parseInt(num / pageSize) + 1;
            } else {
                totalPage = parseInt(num / pageSize);
            }
            var currentPage = pno;//当前页数
            var startRow = (currentPage - 1) * pageSize + 1;//开始显示的行 31
            var endRow = currentPage * pageSize;//结束显示的行  40
            endRow = (endRow > num) ? num : endRow;  //40
            //遍历显示数据实现分页
            for (var i = 1; i < (num + 1); i++) {
                var irow = itemss[i - 1];
                var irow2 = hrs[i - 1];
                if (i >= startRow && i <= endRow) {
                    irow.style.display = "block";
                    irow2.style.display = "block";
                } else {
                    irow.style.display = "none";
                    irow2.style.display = "none";
                }
            }

            var tempStr = `<div style="margin-left: 50%; margin-top: 20px; margin-right:-174px; margin-bottom: 40px; font-size: large">` + "总计 " + all_num + " 条； 分" + totalPage + "页 当前 第 " + currentPage + " 页";
            if (currentPage > 1) {
                tempStr += `<a href="#" onClick="goPage(1,${psize} ,'${tagName}')"> 首页 </a>`;
                tempStr += `<a href="#" onClick="goPage(${currentPage - 1},${psize} ,'${tagName}')"> <上一页 </a>`;
            } else {
                tempStr += " 首页 ";
                tempStr += " <上一页 ";
            }
            if (currentPage < totalPage) {
                tempStr += `<a href="#" onClick="goPage(${currentPage + 1},${psize} ,'${tagName}')"> 下一页> </a>`;
                tempStr += `<a href="#" onClick="goPage(${totalPage},${psize} ,'${tagName}')"> 尾页 </a>`;
            } else {
                tempStr += " 下一页> ";
                tempStr += " 尾页 ";
            }
            tempStr += "</div>";
            document.getElementById("barcon").innerHTML = tempStr;
        };

        goPageAll(1, 20, "全部");
    </script>
    </body>
    </html>"""

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
    tags = set()
    article_str = """"""
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
        if first_tag:
            for first_tag_temp in first_tag.split(","):
                if first_tag_temp not in tags:
                    tags.add(first_tag_temp)

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
        if len(brief_content) > 260:
            brief_content = brief_content[:260]

        article_str += template_str.format(link, title, brief_content, add_time, first_tag, second_tag)

    tag_str = ""

    for tag in tags:
        tag_str += """<span class="tag" id="{}" style="border-width: 2px; padding: 3px 10px 3px 10px; "><a href="#" onclick="goPage(1, 20, '{}')">{}</a></span>""".format(
            tag, tag, tag)
    html_str = html_str + tag_str + """</div>
    <ul>""" + article_str + tail_str
    with open(output_file, mode="w+") as f:
        f.write(html_str)

    print(f"提取成功!保存至{output_file}")


if __name__ == "__main__":
    create_html()
