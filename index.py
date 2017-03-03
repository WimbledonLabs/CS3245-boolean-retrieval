#!/usr/bin/env python3
from pprint import pprint
import os
import argparse
import nltk

from collections import defaultdict

from serde import serialize, deserialize
from skiplist import skiplist

stemmer = nltk.stem.PorterStemmer()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--source", required=True)
parser.add_argument("-d", "--dictionary", required=True)
parser.add_argument("-p", "--postings", required=True)

args = parser.parse_args()
document_dir = args.source

index = defaultdict(set)

#================================================
# Essay question helper functions
#================================================
numbers = "0123456789.-+,"
def normalize(word):
    if not all(c in numbers for c in word):
        return word

    # Remove commas
    word = "".join(word.split(','))
    isfloat = False

    try:
        f = float(word)
        isfloat = True
        i = int(word)
        isint = True

        # Preserve years
        if 1800 < i < 2100:
            return str(i)

    except ValueError:
        pass

    # Limit the number of significant digits
    if isfloat:
        return "%.2g" % f

    return word

def skipword(word):
    if len(word) < 2:
        return True
    if word in ['of', 'to', 'the', 'and', 'in', 'a', 'it', 'for', 'on', "'s", 'is', 'by', 'from']:
        return True
    return False

#================================================
# Main Code
#================================================

for document_name in os.listdir(document_dir):
    with open(os.path.join(document_dir, document_name)) as document:
        doc = document.read().lower()
        doc_id = int(document_name)
        index["ALL_DOCS"].add(doc_id)
        for sentence in nltk.sent_tokenize(doc):
            print(repr(sentence), '\n')
            for word in nltk.word_tokenize(sentence):
                word = stemmer.stem(word)
                ''' 
                # Rough work for essay questions
                word = normalize(word)
                if skipword(word):
                    continue
                '''
                index[word].add(doc_id)

dictionary = {}

with open(args.postings, 'wb') as postings_file:
    for word, docs in index.items():
        s = serialize(skiplist(sorted(list(docs))))
        dictionary[word] = (len(docs), len(s), postings_file.tell())
        postings_file.write(s)

with open(args.dictionary, 'wb') as dict_file:
    dict_file.write(serialize(dictionary))

