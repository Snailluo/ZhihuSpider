import os
import re
import win32api

import time

import tool.tomd as tomd
from urllib import parse

import requests
import win32con


def get_desktop():
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                              r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',
                              0, win32con.KEY_READ)
    return win32api.RegQueryValueEx(key, 'Desktop')[0]


# 设置cookies
def init(session_url):
    ua = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/"
                      "537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20"
    }

    s = requests.session()
    s.headers.update(ua)
    text = s.get(session_url)
    name = re.compile("(?<=data-react-helmet=\"true\">).+?(?=</title>)")
    return s, name.findall(text.text)


def get_answer_data(s, answer_url, limit, offset):
    url_code = "data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2" \
               "Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2" \
               "Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2" \
               "Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2" \
               "Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2" \
               "Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2" \
               "Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2" \
               "A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics"
    include = parse.unquote(url_code)
    # print(include)

    params = {
        "include": include,
        "limit": limit,
        "offset": offset
    }

    return s.get(answer_url, params=params)


def get_imgurl(content):

    imgRe = re.compile(r"(https://[^\s]*?_r\.(jpg|png|gif|jpeg))")
    imgList = imgRe.findall(content)
    imgList = list(set(imgList))

    imgUrls = []
    for url in imgList:
        imgUrls.append(url[0])

    return imgUrls


def create_folder(path, folder_name):
    if path[-1] != "\\":
        path = path + "\\"
    author_local_path = path + folder_name + "\\"
    if not os.path.exists(author_local_path):
        os.mkdir(author_local_path)
    return author_local_path


def download(download_url, download_path):
    name = download_url.split("/")[-1]
    img_path = download_path + name

    if not os.path.exists(img_path):
        img_res = requests.get(download_url)
        if img_res.status_code == requests.codes.ok:

            with open(img_path, 'wb') as f:
                f.write(img_res.content)
                print("download:", img_path)

            # return True
        else:
            time.sleep(0.5)
            print("error:", download_url)
            # download(download_url, download_path)
            # print(img_res.status_code)
            # print(img_res.headers)
            # print(img_res.text)
            # return False
    else:
        print("exit:", img_path)
    

def html2md(content_html):
    content_md = tomd.convert(content_html)
    if content_md != '':
        return content_md
    else:
        return content_html


def save_answer(content, author_path, author_name):
    # answer_md = tomd.convert(content)
    answer_localpath = author_path + author_name + ".md"
    if os.path.exists(answer_localpath):
        print("exit:", answer_localpath)
    else:
        with open(answer_localpath, 'w', encoding='utf-8') as f:
            f.write(html2md(content))
        print("save answer:", answer_localpath)
            # f.write(answer_md)
