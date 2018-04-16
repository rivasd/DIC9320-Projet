import lucene
import os

for TrecFile in os.listdir("./AP"):
    with open(os.path.abspath(os.path.join("AP",TrecFile)), 'r') as docfile:
        docfile
