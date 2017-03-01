#!/usr/bin/env python3
from pprint import pprint
import os
import argparse
import nltk

from collections import defaultdict

from serde import serialize, deserialize

stemmer = nltk.stem.PorterStemmer()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--source", required=True)
parser.add_argument("-d", "--dictionary", required=True)
parser.add_argument("-p", "--postings", required=True)

args = parser.parse_args()
document_dir = args.source

index = defaultdict(set)

for document_name in os.listdir(document_dir):
    with open(os.path.join(document_dir, document_name)) as document:
        doc_id = int(document_name)
        index["ALL_DOCS"].add(doc_id)
        for sentence in nltk.sent_tokenize(document.read().lower()):
            for word in nltk.word_tokenize(sentence):
                index[stemmer.stem(word)].add(doc_id)

dictionary = defaultdict(tuple)

with open(args.postings, 'wb') as postings_file:
    for word, docs in index.items():
        s = serialize(sorted(list(docs)))
        dictionary[word] = (len(docs), len(s), postings_file.tell())
        postings_file.write(s)

with open(args.dictionary, 'wb') as dict_file:
    dict_file.write(serialize(dictionary))
