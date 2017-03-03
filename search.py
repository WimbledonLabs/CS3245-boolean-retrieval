#!/usr/bin/env python3
from pprint import pprint
import os
import argparse
import nltk

from collections import defaultdict
from serde import serialize, deserialize

import re
import operator

from skiplist import skiplist

from functools import reduce

TERM_TOTAL = 1000
stemmer = nltk.stem.PorterStemmer()

#================================================
# AST Classes
#================================================

class Expr():
    def __init__(self, *children):
        self.children = list(children)

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, tuple(self.children))

class Not(Expr):
    def compute(self, dictionary, postings_file):
        # Remove the values of this list from the corpus to perform NOT
        return corpus - self.children[0].compute(dictionary, postings_file)

class And(Expr):
    def compute(self, dict_file, postings):
        inputs = [c.compute(dict_file, postings) for c in self.children]

        # It's best to sort by length first since that reduces the number of
        # passes through long lists since len("a AND b") <= min(len("a", len("b"))
        inputs = sorted(inputs, key=len)

        # Perform lista & listb on all the inputs
        return reduce(operator.__and__, inputs)

class Or(Expr):
    def compute(self, dict_file, postings):
        inputs = [c.compute(dict_file, postings) for c in self.children]
        # It's best to sort by length first since that reduces  the number of
        # passes through the lists (this isn't as useful compared to the AND
        # operator, but it should still make a difference, considering the case
        # where you start with one very long list, and merge with a bunch of
        # smaller ones)
        inputs = sorted(inputs, key=len)

        # Perform lista | listb on all the inputs
        return reduce(operator.__or__, inputs)

class Word():
    def __init__(self, word):
        self.word = stemmer.stem(word)

    def __repr__(self):
        return repr(self.word)

    def compute(self, dictionary, postings_file):
        # Get the skiplist for this term from its posting if the term exists
        if self.word in dictionary:
            count, size, pos = dictionary[self.word]
            postings_file.seek(pos)
            return deserialize(postings_file.read(size))
        return skiplist()

#================================================
# Query Parsing
#================================================

class Lexer():
    """ Splits a query string into a stream tokens. The token at the head of the
    stream can be compared to a provided token, and consumed by a parser. """
    def __init__(self, query):
        self.terms = list(reversed(re.findall("\(|\)|[a-zA-Z0-9\.']+", query)))

    def inspect(self, token):
        """ Return True if the current token equals the provided token """
        # If there are still tokens left
        if self.terms:
            return self.terms[-1] == token
        return False

    def consume(self, token):
        """ Return move to the next token and return True if the current token
        equals the provided token """
        if self.inspect(token):
            self.terms.pop()
            return True
        return False

    def next(self):
        """ Return the token at the head of the stream, and move to the next token """
        return self.terms.pop()


def parse_query(query):
    """ Parse the well-formed query string into an AST of Not, And, Or, and
    Word objects using a recursive descent parser, using the following
    grammar:

    Program: Expr$
       Expr: Term ("OR" Term)*
       Term: Factor ("AND" Factor)*
     Factor: "NOT" Factor
            | "(" Expr ")"
            | Id
         Id: [a-zA-Z0-0]+

    The parsing functions which represent this grammar are not commented since
    they are a straight translation from this grammar to code"""
    # The lexer is a global variable to avoid the ugliness of passing it around
    # everywhere (could be avoided by using a parsing object, but that's work
    # for little gain)
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
        return Not(factor())
    elif lexer.consume("("):
        e = expr()
        lexer.consume(")")
        return e
    else:
        return id()

def id():
    return Word(lexer.next())

#================================================
# Main Search Logic
#================================================

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

# Get the list of all documents in the corpus so we can perform NOT
# operations on skiplists
count, size, pos = dictionary["ALL_DOCS"]
postings_file.seek(pos)
corpus = deserialize(postings_file.read(size))

# Write out the results of each query to the output
for query in query_file:
    # Remove trailing whitespace from the query line
    query = query.strip()
    print(parse_query(query))
    result = parse_query(query).compute(dictionary, postings_file)
    output.write(" ".join(str(i) for i in result) + '\n')
