import os
import time
from configparser import ConfigParser

from util import get_desktop, init, get_answer_data, get_imgurl, download, create_folder, save_answer

if __name__ == "__main__":

    conf = ConfigParser()
    conf.read("config\\path.conf", encoding="utf-8")
    qid = conf.get("setting", "qid")
    conf.clear()

    url = "https://www.zhihu.com/question/" + qid
    answer_url = "https://www.zhihu.com/api/v4/questions/" + qid + "/answers"
    # print(answer_url)

    val = init(url)

    session = val[0]
    question_name = val[1]

    # localPath = get_desktop() + "\\" + question_name[0] + "\\"
    # print(localPath)
    # if not os.path.exists(localPath):
    #     os.mkdir(localPath)

    localPath = create_folder(get_desktop(), question_name[0])

    is_end = False
    start = 0

    while not is_end:
        answer_res = get_answer_data(session, answer_url, 5, start)

        data = answer_res.json()['data']
        is_end = answer_res.json()['paging']['is_end']
        start += 5

        for answer in data:
            imgs = get_imgurl(answer['content'])
            author = answer['author']
            if author['name'] == "匿名用户" or author['name'] == "知乎用户":
                author['name'] = author['name'] + str(answer['id'])
            author_download_path = create_folder(localPath, author['name'])
            if imgs:
                for img in imgs:
                    download(img, author_download_path)
                    time.sleep(0.5)
            save_answer(answer['content'], author_download_path, author['name'])
