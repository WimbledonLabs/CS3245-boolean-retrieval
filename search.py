#!/usr/bin/env python3
from pprint import pprint
import os
import argparse
import nltk

from collections import defaultdict
from serde import serialize, deserialize

import re

TERM_TOTAL = 1000
stemmer = nltk.stem.PorterStemmer()

# TBD, this should be a super-awesome skip list
ALL_DOCS = []

def mergeUnion(*doc_lists):
    result = doc_lists[0]
    for child in doc_lists[1:]:
        a = result
        b = child
        result = []

        cursor_a = 0
        cursor_b = 0

        while cursor_a < len(a) or cursor_b < len(b):
            if cursor_a == len(a):
                # We are at the end of list a, grab all of the rest of list b
                result.extend(b[cursor_b:])
                break

            elif cursor_b == len(b):
                # We are at the end of list b, grab all of the rest of list a
                result.extend(b[cursor_a:])
                break

            elif a[cursor_a] < b[cursor_b]:
                result.append(a[cursor_a])
                cursor_a += 1
            elif a[cursor_a] > b[cursor_b]:
                result.append(b[cursor_b])
                cursor_b += 1
            elif a[cursor_a] == b[cursor_b]:
                result.append(a[cursor_a])
                cursor_a += 1
                cursor_b += 1
    return result

def mergeIntersection(*doc_lists):
    result = doc_lists[0]
    for child in doc_lists[1:]:
        a = result
        b = child
        result = []

        cursor_a = 0
        cursor_b = 0

        while cursor_a < len(a) and cursor_b < len(b):
            if a[cursor_a] < b[cursor_b]:
                cursor_a += 1
            elif a[cursor_a] > b[cursor_b]:
                cursor_b += 1
            elif a[cursor_a] == b[cursor_b]:
                result.append(a[cursor_a])
                cursor_a += 1
                cursor_b += 1
    return result

def invert(docs):
    return list(doc for doc in ALL_DOCS if doc not in docs)

class Lexer():
    def __init__(self, query):
        self.terms = list(reversed(re.findall("\(|\)|AND|OR|[a-zA-Z]+", query)))
        #print(self.terms)

    def inspect(self, token):
        if self.terms:
            return self.terms[-1] == token
        return False

    def consume(self, token):
        if self.inspect(token):
            self.terms.pop()
            return True
        return False

    def next(self):
        return self.terms.pop()

class Expr():
    def __init__(self, *children):
        self.children = list(children)

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, tuple(self.children))

class Not(Expr):
    def compute(self, dictionary, postings_file):
        return invert(self.children[0].compute(dictionary, postings_file))

    def __len__(self):
        return TERM_TOTAL - len(self.children[0])

class And(Expr):
    def compute(self, dict_file, postings):
        inputs = [c.compute(dict_file, postings) for c in self.children]

        # It's best to sort by length first since that reduces
        # the number of passes through the lists
        inputs = sorted(inputs, key=lambda x: len(x))

        return mergeIntersection(*inputs)

    def __len__(self):
        # Worst case estimate is that they're all the same
        return max(len(c) for c in self.children)

class Or(Expr):
    def compute(self, dict_file, postings):
        # It's best to sort by length first since that reduces  the number of
        # passes through the lists (this isn't as useful compared to the AND
        # operator, but it should still make a difference, considering the case
        # where you start with one very long list, and merge with a bunch of
        # smaller ones)
        inputs = [c.compute(dict_file, postings) for c in self.children]
        inputs = sorted(inputs, key=lambda x: len(x))
        return mergeUnion(*inputs)

    def __len__(self):
        # Worst case estimate is that they're all disjoint
        return sum(len(c) for c in self.children)

class Word():
    def __init__(self, word):
        self.word = word

    def __repr__(self):
        return repr(self.word)

    def compute(self, dictionary, postings_file):
        key = stemmer.stem(self.word)
        if key in dictionary:
            count, size, pos = dictionary[key]
            postings_file.seek(pos)
            return deserialize(postings_file.read(size))
        return []

    def __len__(self):
        # Worst case estimate is that they're all disjoint
        return sum(len(c) for c in self.children)


def parse_query(query):
    global lexer
    lexer = Lexer(query)
    return expr()

def expr():
    e = term()
    if lexer.consume("OR"):
        e = Or(e, term())
        while lexer.consume("OR"):
            e.children.append(term())
    return e

def term():
    e = factor()
    if lexer.consume("AND"):
        e = And(e, factor())
        while lexer.consume("AND"):
            e.children.append(factor())
    return e

def factor():
    if lexer.consume("NOT"):
        return Not(expr())
    elif lexer.consume("("):
        e = expr()
        lexer.consume(")")
        return e
    else:
        return id()

def id():
    return Word(lexer.next())


# search.py -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dictionary", required=True)
parser.add_argument("-p", "--postings", required=True)
parser.add_argument("-q", "--query", required=True)
parser.add_argument("-o", "--output", required=True)

args = parser.parse_args()

postings_file = open(args.postings, 'rb')
dict_file = open(args.dictionary, 'rb')
query_file = open(args.query)
output = open(args.output, 'w')

dictionary = deserialize(dict_file.read())

count, size, pos = dictionary["ALL_DOCS"]
postings_file.seek(pos)
ALL_DOCS = deserialize(postings_file.read(size))

for query in query_file:
    query = query.strip()
    result = parse_query(query).compute(dictionary, postings_file)
    output.write("\n".join(str(i) for i in result) + '\n')
