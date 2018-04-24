
import os
from collections import OrderedDict

import lucene

from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader, IndexReader
from org.apache.lucene.search import IndexSearcher, Query, TopDocs
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory

from Analyzers import BaselineAnalyzer, BetterAnalyzer
from Indexer import printProgressBar

from org.apache.lucene.search.similarities import ClassicSimilarity, BM25Similarity


class Search(object):

    querystoplist = ["Document", "will", "must", "identify", "discuss", "discusses", "mention", "contain", "cites", "identify", "refers"]

    def __init__(self, dir, requetes, expander=None):
        self.dir = dir
        self.requetes = requetes
        if expander:
            self.expander= expander

        javaDir = SimpleFSDirectory(Paths.get(os.path.join("./Indexes"), self.dir))

        self.reader         = DirectoryReader.open(javaDir)
        self.searcher       = IndexSearcher(self.reader)
        
        analyzer, similarity = dir.split("_")
        self.analyzer   = BetterAnalyzer() if analyzer.lower() == "better" else BaselineAnalyzer()
        self.similarity = BM25Similarity() if similarity.lower() == "bm25" else ClassicSimilarity()

        self.queryparser    = QueryParser("text", self.analyzer)
        self.searcher.setSimilarity(self.similarity)
    
    def build_queries(self):
        
        queries = OrderedDict()

        with open(os.path.join("./requetes",self.requetes), 'r') as req_file:
            for line in req_file:
                elems = [elem.strip() for elem in line.split("#")]
                if len(elems) > 2:

                    # remove the frequent useless words from the query that merely state that a query is being made
                    for querystopword in self.querystoplist:
                        elems[2].replace(querystopword, "")
                    
                    # concatenate the short and big query to make the final query
                    query = elems[1] + " " + elems[2]
                else:
                    query = elems[1]
                
                query = self.queryparser.escape(query)
                queries[elems[0]] = self.queryparser.parse(query)
        
        return queries

    def execute(self):
        queries = self.build_queries()
        results = []
        count = 1

        for query_num, query in queries.items():

            printProgressBar(count, 50, prefix=("query:"+str(count)))


            scoreDocs = self.searcher.search(query, 1000).scoreDocs

            for idx, scoreDoc in enumerate(scoreDocs):
                doc = self.searcher.doc(scoreDoc.doc)
                docno   = doc.get('docno')
                sim     = scoreDoc.score
                rank    = idx
                run     = "Daniel_Rivas_DIC9320_Hiver_2018"

                results.append({
                    'query_num':str(count),
                    'docno':docno,
                    'sim':sim,
                    'rank':rank,
                    'iter': '0',
                    'run': run
                })
            count +=1
        
        print("search complete, now writing to file...")
        return results

    def to_file(self, file_name):
        
        results = self.execute()

        if not os.path.isdir("./results"):
            os.mkdir("./results")

        with open(os.path.join("./results", file_name), 'wt') as res_file:
            for idx, result in enumerate(results):

                printProgressBar(idx+1, len(results), prefix="        ")

                line = "%s %s %s %s %s %s\n" % (result["query_num"], result["iter"], result["docno"], result["rank"], result["sim"], result["run"])
                res_file.write(line)





if __name__ == "__main__":

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    for analyzer in ['baseline', 'better']:
        for similarity in ['classic', 'bm25']:
            for requete in ['Courtes', 'Longues']:
                search = Search(analyzer+"_"+similarity, "requetes"+requete+".txt")

                print("Compiling search results for model: \n%s analyzer | %s similarity | requetes %s" % (analyzer, similarity, requete ) )

                search.to_file(analyzer+"_"+similarity+"_"+requete.lower()+".txt")

                print("Done\n")
