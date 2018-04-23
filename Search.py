
import os

from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader, IndexReader
from org.apache.lucene.search import IndexSearcher, Query, ScoreDoc, TopDocs
from org.apache.lucene.queryparser.classic import QueryParser

from .Analyzers import BaselineAnalyzer, BetterAnalyzer

from org.apache.lucene.search.similarities import ClassicSimilarity, BM25Similarity


class Results(object):

    def __init__(self, dir, requetes, expander=None):
        self.dir = dir
        self.requetes = requetes
        if expander:
            self.expander= expander

        self.reader         = DirectoryReader(Paths.get(os.path.join("./Indexes"), self.dir))
        self.searcher       = IndexSearcher(self.reader)
        
        analyzer, similarity = dir.split("_")
        self.analyzer   = BetterAnalyzer() if analyzer.lower() == "better" else BaselineAnalyzer()
        self.similarity = BM25Similarity() if similarity.lower() == "bm25" else ClassicSimilarity()

        self.queryparser    = QueryParser("text", self.analyzer)
        self.searcher.setSimilarity(self.similarity)
    


    
