#!/usr/bin/env python3
from pprint import pprint
import os
import argparse
import nltk

import file

from collections import defaultdict

def numSkips(count):
    return floor(count**0.5)

def deserialize(posting, file):
    word, length, offset = posting
    skip_count = numSkips(length)

    file.seek(offset)

    for i in range(skip_count + length):
        if i % (skip_count + 1) == 0:
            # This is the skip pointer
            i = file.read(2)
            i = i[0] << 8 | i[1]


            if something:
                # Take the pointer
                file.seek(2*skip_count, io.SEEK_CUR)
        else:
            yield file.read(2)
            # file.seek(2, io.SEEK_CUR)


def serialize(index, postings, file):
    for word, ids in index.items():
        length = len(ids)
        skip_count = numSkips(length)

        postings[word] = (length, file.tell())

        for i, id in enumerate(ids):
            if i % skip_count == 0:
                file.write(bytes([ids[i+skip_count] >> 8,
                                  ids[i+skip_count] & 255]))
            file.write(bytes([id >> 8, id & 255]))



'''
[ 4sk, 0,   1,  2,  3,
  8sk  4,   5,  6,  7,
 12sk  8,   9, 10, 11,
 15sk  12, 13, 14]
'''


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--source", required=True)
parser.add_argument("-d", "--dictionary", required=True)
parser.add_argument("-p", "--posting", required=True)

args = parser.parse_args()

print(args)

document_dir = args.source

index = defaultdict(set)

stemmer = nltk.stem.PorterStemmer()

for document_name in os.listdir(document_dir):
    with open(os.path.join(document_dir, document_name)) as document:
        for sentence in nltk.sent_tokenize(document.read().lower()):
            print(sentence)
            for word in nltk.word_tokenize(sentence):
                index[stemmer.stem(word)].add(document_name)
pprint(index)
