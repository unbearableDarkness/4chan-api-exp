import requests
import random
import html
import re
import json
import time

boards = ["a", "b", "c", "d", "e", "f", "g", "gif", "h", "hr", "k", "m", "o", "p", "r", "s", "t", "u", "v", "vg", "vm",
          "vmg", "vr", "vrpg", "vst", "w", "wg", "i", "ic", "r9k", "s4s", "vip", "qa", "cm", "hm", "lgbt", "y", "3",
          "aco", "adv", "an", "bant", "biz", "cgl", "ck", "co", "diy", "fa", "fit", "gd", "hc", "his", "int", "jp",
          "lit", "mlp", "mu", "n", "news", "out", "po", "pol", "pw", "qst", "sci", "soc", "sp", "tg", "toy", "trv",
          "tv", "vp", "vt", "wsg", "wsr", "x", "xs"]

sfw_boards = ["a", "c", "g", "k", "m", "o", "p", "v", "vg", "vm", "vmg", "vr", "vrpg", "vst", "w", "vip", "qa", "cm",
              "lgbt", "3", "adv", "an", "biz", "cgl", "ck", "co", "diy", "fa", "fit", "gd", "his", "int", "jp", "lit",
              "mlp", "mu", "n", "news", "out", "po", "pw", "qst", "sci", "sp", "tg", "toy", "trv", "tv", "vp", "vt",
              "wsg", "wsr", "x", "xs"]




# \s matches whitespace (spaces, tabs and new lines). \S is negated \s.
def process_comment(s):
    s = html.unescape(s)
    s = re.sub("(<a.*?</a>)", "", s)
    s = re.sub('<span class="quote">>(.*?)</span>', '\g<1>', s)
    s = re.sub('<br>', "\n", s)
    s = re.sub('\'', '', s)
    s = re.sub('<(.*?)>?(.*?)</(.*?)', '\g<2>', s)
    s = re.sub('https?\S+', "", s)
    s = re.sub('[^\w\s]', '', s)
    return s


def search(board, search_str):
    print("Searching for '{0}' on the board '{1}'.".format(search_str, board))
    response = requests.get("https://a.4cdn.org/{0}/catalog.json".format(board))
    data = json.loads(response.text)

    # list that will contain the thread/posts that contain the certain string
    # [(threadID, postID)] -> only 1 entry if the the post is a thread
    found = []
    found_urls = []
    i = 0

    for page_data in data:
        for thread in page_data["threads"]:
            if "sticky" not in thread:
                thread_endpoint = "https://a.4cdn.org/{0}/thread/{1}.json".format(board, thread["no"])
                thread_response = requests.get(thread_endpoint)
                thread_data = json.loads(thread_response.text)
                for post in thread_data["posts"]:
                    cc = 0
                    for word in search_str.split():
                        if "com" in post:
                            for p_word in process_comment(post["com"]).split():
                                if word == p_word:
                                    cc += 1
                                    if cc == len(search_str.split()):
                                        if "replies" in post:
                                            found.append([thread["no"]])
                                            i += 1
                                        else:
                                            found.append([thread["no"], post["no"]])
                                            i += 1

    for elem in found:
        # a thread
        if len(elem) == 1:
            if board in sfw_boards:
                found_urls.append("https://boards.4channel.org/{0}/thread/{1}".format(board, elem[0]))
            else:
                found_urls.append("https://boards.4chan.org/{0}/thread/{1}".format(board, elem[0]))
        # a post inside a thread
        elif len(elem) == 2:
            if board in sfw_boards:
                found_urls.append("https://boards.4channel.org/{0}/thread/{1}#p{2}".format(board, elem[0], elem[1]))
            else:
                found_urls.append("https://boards.4chan.org/{0}/thread/{1}#p{2}".format(board, elem[0], elem[1]))

    print("\nFound {0} matches.".format(i))
    for j in range(len(found_urls) - 1):
        print(found_urls[j], end='')
        print('\n', end='')


if __name__ == '__main__':
    idx = input("Choose the board: ")
    if not idx.isdigit():
        print("Error, the index must be an integer.")
        exit(-1)
    idx = int(idx)
    if idx < 0 or idx > len(boards) - 1:
        print("Error, the index must be between 0 and {0}".format(len(boards) - 1))
        exit(-1)
    search_string = input("Now enter the string that you want to search for: ")
    t0 = time.time()
    search(boards[idx], search_string)
    t1 = time.time()
    t2 = t1 - t0
    print("\nTime taken: {0} seconds. ".format(round(t2)))
