import argparse

parser = argparse.ArgumentParser()
parser.add_argument("b")
parser.add_argument("a")

args = parser.parse_args()

with open(args.a) as a:
    a_docs = set(a.readline().split())

with open(args.b) as b:
    b_docs = set(b.readline().split())

diff = a_docs ^ b_docs

for doc in sorted(diff):
    if doc in a_docs:
        print("<<< %s" % doc)
    else:
        print(">>> %s" % doc)
