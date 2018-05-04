import os
import requests
import re
from urllib import parse
from configparser import ConfigParser

import win32api

import time
import win32con


def get_Desktop():
    key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,\
                              r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',\
                              0,win32con.KEY_READ)
    return win32api.RegQueryValueEx(key, 'Desktop')[0]

# 设置cookies
def init(url):
    ua = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20"
    }
    s = requests.session()
    s.headers.update(ua)
    text = s.get(url)
    name = re.compile("(?<=data-react-helmet=\"true\">).+?(?=</title>)")
    return s, name.findall(text.text)

def get_answer_data(s, qid, answer_url, limit, offset):

    url_code = "data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics"
    include = parse.unquote(url_code)
    # print(include)

    params = {
        "include": include,
        "limit": limit,
        "offset": offset
    }

    return s.get(answer_url, params=params)

def get_imgUrl(content):
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
    author_path = localPath + "/" + author_name + "/"
    if not os.path.exists(author_path):
        os.mkdir(author_path)
    return author_path

def download(url, localPath):

    img_req = requests.get(url)
    if img_req.status_code == requests.codes.ok:
        name = url.split("/")[-1]
        with open(localPath+name,'wb') as f:
            f.write(img_req.content)
            print("download:", url)
        return True
    else:
        print("error:", url)
        print(img_req.status_code)
        return False

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

    localPath = get_Desktop() + "/" + question_name[0] + "/"
    print(localPath)
    if not os.path.exists(localPath):
        os.mkdir(localPath)

    is_end = False
    offset = 0

    while not is_end:
        answer_req = get_answer_data(session, qid, answer_url, 5, offset)

        data = answer_req.json()['data']
        is_end = answer_req.json()['paging']['is_end']
        offset +=5

        for answer in data:
            imgs = get_imgUrl(answer['content'])
            if imgs:
                author = answer['author']
                author_path = create_author_path(localPath, author['name'])
                print(imgs)
                for img in imgs:
                    download(img, author_path)
                    time.sleep(0.1)