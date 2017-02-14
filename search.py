#!/usr/bin/env python3
from pprint import pprint
import os
import argparse
import nltk

from collections import defaultdict
from serde import serialize, deserialize

import re

"""
def parse_query_re(query):
    # Since there are no nested brackets, this is a regular grammar, which
    # means that we can parse it with just a regex :D :D :D
    terms = re.split(r'(\([a-z ]*\))', query, flags=re.IGNORECASE)

    return terms


def parse_query(query):
    out = []
    op = []
    tokens = re.split(r'(\([a-z ]*\))', query, flags=re.IGNORECASE)
    for token in tokens:
        if token == "AND":
            pass
        elif token == "OR":
            pass
        elif token == "NOT":
            pass

        if token.startswith('('):
            val = parse_query(token[1:-1])
        else:
            val = token
"""

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
        self.children = children

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, tuple(self.children))

class Not(Expr):
    pass

class And(Expr):
    pass

class Or(Expr):
    pass

class Word():
    def __init__(self, word):
        self.word = word

    def __repr__(self):
        return repr(self.word)


def parse_query(query):
    global lexer
    lexer = Lexer(query)
    return expr()

def expr():
    e = term()
    while lexer.consume("OR"):
        e = Or(e, term())
    return e

def term():
    e = factor()
    while lexer.consume("AND"):
        e = And(e, factor())
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
dictionary_file = open(args.dictionary, 'rb')
query_file = open(args.query)
postings = deserialize(postings_file.read())

for query in query_file:
    '''
    doc_count, length, pos = postings[word.strip()]
    dictionary_file.seek(pos)
    print(deserialize(dictionary_file.read(length)))
    '''
    query = query.strip()
    print(query)
    print(parse_query(query))
    print('\n\n')
