
import collections
import wordcloud
import requests
import datetime
import numpy
import html
import json
import re
import os
import csv
import time

from wordcloud import WordCloud, STOPWORDS
from PIL import Image

boards = ["a", "b", "c", "d", "e", "f", "g", "gif", "h", "hr", "k", "m", "o", "p", "r", "s", "t", "u", "v", "vg", "vm",
          "vmg", "vr", "vrpg", "vst", "w", "wg", "i", "ic", "r9k", "s4s", "vip", "qa", "cm", "hm", "lgbt", "y", "3",
          "aco", "adv", "an", "bant", "biz",  "cgl", "ck", "co", "diy", "fa", "fit", "gd", "hc", "his", "int", "jp",
          "lit", "mlp", "mu", "n", "news", "out", "po", "pol", "pw", "qst", "sci", "soc", "sp", "tg", "toy", "trv",
          "tv", "vp", "vt", "wsg", "wsr", "x", "xs"]

common_words = ["have", "had", "the", "did", "dont", "be", "to", "of", "and", "a", "in", "that", "have", "I", "it",
                "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they",
                "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
                "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like",
                "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could",
                "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
                "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want",
                "because", "any", "these", "give", "day", "most", "us", "has", "really", "still"]


# \s matches whitespace (spaces, tabs and new lines). \S is negated \s.
def process_comment(s):
    s = html.unescape(s)
    s = re.sub("(<a.*?</a>)", "", s)
    s = re.sub('<span class="quote">>(.*?)</span>', '\g<1>', s)
    s = re.sub('<br>',"", s)
    s = re.sub('\'', '', s)
    s = re.sub('<(.*?)>?(.*?)</(.*?)','\g<2>', s)
    s = re.sub('https?\S+', "", s)
    s = re.sub('[^\w\s]','', s)
    return s


def get_words(board):
    url = "https://a.4cdn.org/{0}/catalog.json".format(board)
    response = requests.get(url)
    # json -> dictionary
    # get the json object
    data = json.loads(response.text)

    word_list = []

    # here we scrape the information
    # page_data = array object of objects of the json data
    # thread = array object of objects of page_data

    total_comments = []
    for page_data in data:
        for thread in page_data["threads"]:
            comments = []
            if "sticky" not in thread:
                thread_endpoint = "https://a.4cdn.org/{0}/thread/{1}.json".format(board, thread["no"])
                thread_response = requests.get(thread_endpoint)
                thread_data = json.loads(thread_response.text)
                for post in thread_data["posts"]:
                    if "com" in post:
                        comments.append(post["com"])
                total_comments.append(comments)

    # remove all the unnecessary characters
    total_comments = [process_comment(x) for comments in total_comments for x in comments]
    # filter out empty sublists in our list of lists
    total_comments = filter(None, total_comments)
    numpy.set_printoptions(threshold=numpy.inf)

    # extract single words from our list of lists of words
    # filter out the words that have less than 4 chars
    minlenght = 2
    for sublist in total_comments:
        for word in sublist.split():
            if len(word) > minlenght:
                word_list.append(word)
                # this is our word list for the wordcloud

    # remove common words
    word_list = [word for word in word_list if word not in common_words]

    # coounter object
    counter = collections.Counter(word_list)
    print(counter)

    # generate our wordcloud
    generate_wordcloud(word_list, board)


def generate_wordcloud(word_list, board):

    mask_name = "cloud.png"
    mask_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordclouds_masks", mask_name)
    mask = numpy.array(Image.open(mask_image_path))

    # wordcloud
    wc = WordCloud(
        background_color="black",
        mask=mask,
        max_words=1000,
        stopwords=STOPWORDS
    )

    # generate our wordcloud and store the result to a file
    ext = ".png"
    wc.generate(' '.join(word_list))
    image_name = "{0}_{1}{2}".format(board, str(datetime.datetime.now().strftime("%H-%M-%S")), ext)
    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordclouds_images", image_name)
    wc.to_file(res_path)


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
    t0 = time.time()
    get_words(boards[idx])
    t1 = time.time()
    t2 = t1 - t0
    print("\nTime taken: {0} seconds. ".format(round(t2)))


if __name__ == '__main__':
    main()
