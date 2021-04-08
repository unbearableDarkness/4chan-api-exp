import requests
import random
import json
import re

boards = [
    "a",
    "c",
    "g",
    "k",
    "m",
    "o",
    "p",
    "v",
    "vg",
    "vm",
    "vmg",
    "vr",
    "vrpg",
    "vst",
    "w",
    "vip",
    "qa",
    "cm",
    "lgbt",
    "3",
    "adv",
    "an",
    "biz",
    "cg",
    "ck",
    "co",
    "diy",
    "fa",
    "fit",
    "gd",
    "his",
    "int",
    "jp",
    "lit",
    "mlp",
    "mu",
    "n",
    "news",
    "out",
    "po",
    "pw",
    "qst",
    "sci",
    "sp",
    "tg",
    "toy",
    "trv",
    "tv",
    "vp",
    "vt",
    "wsg",
    "wsr",
    "x",
    "xs"
]


def get_last_4chan_id(board):
    idx = random.randint(0, len(_4chan_boards_) - 1)
    response = requests.get("https://a.4cdn.org/" + board + "/catalog.json")
    # json -> dictionary
    # get the json object
    data = json.loads(response.text)

    threads_info = []
    replies_info = []

    for page_data in data:
        for thread in page_data["threads"]:
            if "sticky" not in thread:
                threads_info.append((thread["no"], thread["now"]))
                if thread["replies"] > 0:
                    for reply in thread["last_replies"]:
                        replies_info.append((reply["no"], reply["now"]))

    # sort the posts by date
    [r.sort(key=lambda x: [d for d in x[1] if d.isdigit()]) for r in [threads_info, replies_info]]

    # Get only the digits from the dates and compare them
    # - then return the id associated to that date
    last_thread_date = int(''.join(char for char in threads_info[-1][1] if char.isdigit()))
    last_post_date = int(''.join(char for char in replies_info[-1][1] if char.isdigit()))
    # print(max(last_thread_date, last_post_date))

    if (max(last_thread_date, last_post_date)) == last_thread_date:
        return threads_info[-1][0]
    else:
        return replies_info[-1][0]


def main():
    idx = input("Choose the board: ")
    if not idx.isdigit():
        print("Error, the index must be an integer.")
        exit(-1)
    idx = int(idx)
    if idx < 0 or idx > len(boards) - 1:
        print("Error, the index must be between 0 and {0}".format(len(boards) - 1))
        exit(-1)
    print("Processing information about board: '{0}'\n".format(boards[idx]))
    get_last_4chan_id(boards[idx])


if __name__ == '__main__':
    main()
