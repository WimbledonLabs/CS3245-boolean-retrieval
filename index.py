#!/usr/bin/env python3
from pprint import pprint
import os
import argparse
import nltk

from collections import defaultdict

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
