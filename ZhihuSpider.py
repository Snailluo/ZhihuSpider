import os
import requests
import re
from urllib import parse
from configparser import ConfigParser

import win32api

import time
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
    jpg = re.compile(r"https://[^\s]*?_r\.jpg")
    jpeg = re.compile(r"https://[^\s]*?_r\.jpeg")
    png = re.compile(r"https://[^\s]*?_r\.png")
    gif = re.compile(r"https://[^\s]*?_r\.gif")

    imgUrls = []
    imgUrls.extend(jpg.findall(content))
    imgUrls.extend(jpeg.findall(content))
    imgUrls.extend(png.findall(content))
    imgUrls.extend(gif.findall(content))

    imgUrls = list(set(imgUrls))

    return imgUrls


def create_author_path(localPath, author_name):
    author_local_path = localPath + "\\" + author_name + "\\"
    if not os.path.exists(author_local_path):
        os.mkdir(author_local_path)
    return author_local_path


def download(download_url, author_path):
    
    name = download_url.split("/")[-1]
    img_path = author_path + name
    
    if not os.path.exists(img_path):
        img_res = requests.get(download_url)
        if img_res.status_code == requests.codes.ok:
            
            with open(img_path, 'wb') as f:
                f.write(img_res.content)
                print("download:", download_url)
                
            return True
        else:
            print("error:", download_url)
            # print(img_res.status_code)
            # print(img_res.headers)
            # print(img_res.text)
            return False
    else:
        print("exist:", name)


if __name__ == "__main__":

    conf = ConfigParser()
    conf.read("Path.conf", encoding="utf-8")
    qid = conf.get("setting", "qid")
    conf.clear()

    url = "https://www.zhihu.com/question/" + qid
    answer_url = "https://www.zhihu.com/api/v4/questions/" + qid + "/answers"
    print(answer_url)

    val = init(url)

    session = val[0]
    question_name = val[1]

    localPath = get_desktop() + "\\" + question_name[0] + "\\"
    print(localPath)
    if not os.path.exists(localPath):
        os.mkdir(localPath)

    is_end = False
    start = 0

    while not is_end:
        answer_res = get_answer_data(session, answer_url, 5, start)

        data = answer_res.json()['data']
        is_end = answer_res.json()['paging']['is_end']
        start += 5

        for answer in data:
            imgs = get_imgurl(answer['content'])
            # print(imgs)
            if imgs:
                author = answer['author']
                author_download_path = create_author_path(localPath, author['name'])
                for img in imgs:
                    download(img, author_download_path)
                    time.sleep(0.5)
