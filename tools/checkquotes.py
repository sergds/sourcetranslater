# print lines with more than 4 " (Double quotes) \
# i.e broken strings (Broken by a now fixed(? untested) bug in translater)

import sys

f = open(sys.argv[1], "rt", encoding="utf16")

for l in f:
    if l.count('"') > 4:
        print(l)