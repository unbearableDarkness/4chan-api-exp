import json
import os
import time
import sys
import urllib.request
from collections import deque
from threading import Thread
import requests
from requests import exceptions as rex

boards = ["a", "b", "c", "d", "e", "f", "g", "gif", "h", "hr", "k", "m", "o", "p", "r", "s", "t", "u", "v", "vg", "vm",
          "vmg", "vr", "vrpg", "vst", "w", "wg", "i", "ic", "r9k", "s4s", "vip", "qa", "cm", "hm", "lgbt", "y", "3",
          "aco", "adv", "an", "bant", "biz", "cgl", "ck", "co", "diy", "fa", "fit", "gd", "hc", "his", "int", "jp",
          "lit", "mlp", "mu", "n", "news", "out", "po", "pol", "pw", "qst", "sci", "soc", "sp", "tg", "toy", "trv",
          "tv", "vp", "vt", "wsg", "wsr", "x", "xs"]


IMAGES_ROOT_FOLDER = "images"
THREADS_NUM = 16


class Grabber:
    def __init__(self, dest_path, board, thread_id):
        self.destination_path = dest_path
        self.jobs = deque()
        self.board = board
        self.thread_id = thread_id
        self.producer_running = True
        self.t_threads = []

        for _ in range(THREADS_NUM):
            t = Thread(target=self.consumer, daemon=True)
            t.start()
            self.t_threads.append(t)

    def download(self):
        try:
            thread_endpoint = "https://a.4cdn.org/{0}/thread/{1}.json".format(self.board, self.thread_id)
            thread_response = requests.get(thread_endpoint)
            thread_data = json.loads(thread_response.text)
        except (rex.HTTPError, rex.InvalidURL) as e:
            # noinspection PyUnboundLocalVariable
            print("Could not fetch {1}. {0}\n".format(thread_endpoint, e), end='')
            sys.exit(-1)

        # noinspection PyUnboundLocalVariable
        for post in thread_data["posts"]:
            # timestamp
            if "tim" in post:
                # noinspection PyUnboundLocalVariable
                img_url = "https://i.4cdn.org/{0}/{1}{2}".format(self.board, post["tim"], post["ext"])
                img_name = "{0}{1}".format(post["tim"], post["ext"])
                img_destination_path = os.path.join(destination_path, img_name)
                self.jobs.append((img_url, img_destination_path))
        self.producer_running = False
        for t in self.t_threads:
            t.join()

    def consumer(self):
        while True:
            try:
                el = self.jobs.pop()
                urllib.request.urlretrieve(el[0], el[1])
            except (IndexError, urllib.error.HTTPError):
                # pass
                # print(e, '\n', end='')
                if not self.producer_running:
                    return


if __name__ == '__main__':
    myurl = input("Enter the thread URL: ")

    # https://boards.4channel.org/[board]/threadID[[#bottom|#p[postID] --optional]
    # https://boards.4channel.org/g/12345#bottom
    # https://boards.4channel.org/g/12345#p12345

    try:
        if myurl.split('/')[3] not in boards:
            print("Error, that board doesn't exist.")
            sys.exit(-1)
    except IndexError as ex:
        # print(ex, "\n", end='')
        print("Error, please enter a valid url.\n", end='')
        sys.exit(-1)

    myboard:str = myurl.split('/')[3]
    mythread_id:str = (myurl.split('/')[5]).partition('#')[0]
    directory:str = "{0}-{1}".format(myboard, mythread_id)
    destination_folder:str = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), IMAGES_ROOT_FOLDER)
    destination_path:str = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), IMAGES_ROOT_FOLDER, directory)

    try:
        os.makedirs(destination_folder)
    except FileExistsError:
        pass
    try:
        os.mkdir(destination_path)
    except (FileExistsError, PermissionError) as ex:
        print(ex, '\n', end='')
        sys.exit(-1)

    t1 = time.time()
    g = Grabber(destination_path, myboard, mythread_id)
    g.download()
    nfiles = len([name for name in os.listdir(destination_path)])
    t2 = time.time()
    print("Time taken: {0} seconds. Downloaded {1} images/videos.".format(round(t2 - t1), nfiles))
    sys.exit(0)
