#!/usr/bin/env python3
from pprint import pprint
import os
import argparse
import nltk

from collections import defaultdict

from serde import serialize, deserialize


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--source", required=True)
parser.add_argument("-d", "--dictionary", required=True)
parser.add_argument("-p", "--postings", required=True)

args = parser.parse_args()

document_dir = args.source

index = defaultdict(set)
postings = {}

stemmer = nltk.stem.PorterStemmer()

for document_name in os.listdir(document_dir):
    with open(os.path.join(document_dir, document_name)) as document:
        for sentence in nltk.sent_tokenize(document.read().lower()):
            for word in nltk.word_tokenize(sentence):
                index[stemmer.stem(word)].add(document_name)

dict_file = open(args.dictionary, 'wb')
postings_file = open(args.postings, 'wb')

for word, docs in index.items():
    s = serialize(sorted(list(docs)))
    postings[word] = (len(docs), len(s), dict_file.tell())
    dict_file.write(s)

postings_file.write(serialize(postings))

dict_file.close()
postings_file.close()
