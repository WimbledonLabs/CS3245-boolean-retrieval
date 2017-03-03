This is the README file for E0147972's submission

== Python Version ==
I'm using Python Version 3.5 for this assignment.

== General Notes about this assignment ==

The search and indexing functionality is divided between seach.py and index.py
with the only shared code in skiplist.py and serde.py

skiplist.py contains the skiplist class used for indexing and retrieval.
    - The skiplist mostly acts as a wrapper around a sorted list
    - Skip pointers are represented by tuples where the first item is the value
      at the position in the list and the second item is the value of the item
      being pointed to. The item being pointed to is skiplist.stride() away.
    - This configuration has the benefit of being easy to construct (just
      replacing specific elements in a sorted list), and is fast (not measured,
      but using python's built-in list.insert() method can be an order n
      operation, versus constant time for replacing specific elements)
    - Overloaded the operators for __and__, __or__, and __sub__ to implement
      merging for the AND, OR, and NOT operators. Allows for operators like
      "oil & stock", "price | cost", and "corpus - cash", which is nice to
      use at a high-level from search.py

serde.py wraps the serialization and deserialization of the pickle module

index.py is fairly simple, it just builds the index in-memory then writes the
posting for each term to the postings file. Each posting is serialized as a
skiplist using python's built-in pickle module, and the term for the posting
is mapped to a tuple of (document count, posting length, posting position) in
a dictionary. This entire dictionary is then written to the dictionary file,
also serialized with the pickle module.

search.py implements the boolean expression classes And, Not, and Or, and a
parser for generating a tree from a query string. The classes And and Or act as
n-ary operators, and can have any number of inputs (IE the query
"oil AND stock AND price" could be represented by a single `And` object). This
makes it easy to sort by the size of the inputs when merging skiplists.

The parser for query strings is a recursive descent parser since that is the
type of parser I am used to writing, and it results in fairly small readable
code. The lexer gets tokens using regular expressions and is stored in the
global namespace (ew).


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

README.txt       - this file

ESSAY.txt        - the answers to the provided essay questions

index.py         - indexes a given directory of documents and produces files
                   which can be searched by search.py

search.py        - evaluates a list of boolean queries on the index created
                   by index.py

skiplist.py      - class for building and merging skiplists

serde.py         - wraps the serialization and deserialization of the pickle module

compare.py       - testing script for comparing the output of single queries

tester.py        - a fuzz testing script for skiplists

postings.txt     - the output postings file of index.py on the reuters corpus

dictionary.txt   - the output dictionary file of index.py on the reuters corpus


== Statement of individual work ==

Please initial one of the following statements.

[SHM] I, E0147972, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

N/A

I suggest that I should be graded as follows:
 - I should be graded using the standard grading criteria

== References ==

Python standard library - https://docs.python.org/3.5/
 - For referencing the standard library functions

Forum posts

Timoté Vaucher pointed out an optimization I could make in my lexer regex
(which didn't change the functionality, but made it cleaner)

My own notes for implementing recursive descent parsers (from a previous
compilers course)

