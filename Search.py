
import os
from collections import OrderedDict
import argparse

import lucene

from java.nio.file import Paths
from org.apache.lucene.index import DirectoryReader, IndexReader, MultiFields
from org.apache.lucene.search import IndexSearcher, Query, TopDocs
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import BytesRef, BytesRefIterator


from Analyzers import BaselineAnalyzer, BetterAnalyzer
from Indexer import printProgressBar

from org.apache.lucene.search.similarities import ClassicSimilarity, BM25Similarity


class Search(object):

    querystoplist = ["Document", "will", "must", "identify", "discuss", "discusses", "mention", "contain", "cites", "identify", "refers"]

    def __init__(self, dir, requetes, expander=None, method=None):
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

        if expander:
            self.expander = expander
        if method:
            self.method = method
    
    def build_queries(self):
        
        queries = OrderedDict()

        with open(os.path.join("./requetes", "requetes"+self.requetes.capitalize()+".txt"), 'r') as req_file:
            for line in req_file:
                elems = [elem.strip() for elem in line.split("#")]
                if len(elems) > 2:

                    # remove the frequent useless words from the query that merely state that a query is being made
                    for querystopword in self.querystoplist:
                        elems[2] = elems[2].replace(querystopword, "")
                    
                    # concatenate the short and big query to make the final query
                    query = elems[1] + " " + elems[2]
                else:
                    query = elems[1]
                
                if self.expander:
                    # expand the query using word vectors if available
                    query = self.expander.expand(query, centroid=self.method)

                query = query.replace("/", "\/")
                query = query.strip("\n")
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
                    'query_num':query_num.lstrip("0"),
                    'docno':docno,
                    'sim':sim,
                    'rank':rank,
                    'iter': '0',
                    'run': run
                })
            count +=1
        
        print("search complete, now writing to file...")
        return results

    def to_file(self):
        
        results = self.execute()
        file_name = self.dir + "_"+ self.requetes

        if self.expander:
            file_name += "_expanded"

        if not os.path.isdir("./results"):
            os.mkdir("./results")

        with open(os.path.join("./results", file_name+".txt"), 'wt') as res_file:
            for idx, result in enumerate(results):

                printProgressBar(idx+1, len(results), prefix="        ")

                line = "%s %s %s %s %s %s\n" % (result["query_num"], result["iter"], result["docno"], result["rank"], result["sim"], result["run"])
                res_file.write(line)

    def list_all_words(self, to_file=False):

        dictionary = []

        fields  = MultiFields.getFields(self.reader)
        terms   = fields.terms('text')
        termsEnum= terms.iterator()
        for byteref in BytesRefIterator.cast_(termsEnum):
            word = byteref.utf8ToString()
            dictionary.append(word)

        if to_file:
            dict_path = os.path.join(os.path.dirname(__file__), "terms")

            if not os.path.exists(dict_path):
                os.mkdir(dict_path)
            
            with open(os.path.join(dict_path, self.dir+"_dict.txt"), "wt") as f:
                for term in dictionary:
                    f.write(term+"\n")

        return dictionary

    def simple_search(self, term):
        topdocs =  self.searcher.search(self.queryparser.parse(term), 10).scoreDocs
        for scoreDoc in topdocs:
            doc = self.searcher.doc(scoreDoc.doc)

            print("%s: %s" % (doc.get('docno'), doc.get('head')))


    def expansions_to_file(self):
        queries = OrderedDict()

        with open(self.dir+"_"+self.requetes+"_"+str(self.method)+"_expandedqueries.txt", "wt") as expansions:
            with open(os.path.join("./requetes", "requetes"+self.requetes.capitalize()+".txt"), 'r') as req_file:
                for line in req_file:
                    elems = [elem.strip() for elem in line.split("#")]
                    expansions.write(elems[0]+"\n")
                    if len(elems) > 2:

                        # remove the frequent useless words from the query that merely state that a query is being made
                        for querystopword in self.querystoplist:
                            elems[2] = elems[2].replace(querystopword, "")
                        
                        # concatenate the short and big query to make the final query
                        query = elems[1] + " " + elems[2]
                    else:
                        query = elems[1]

                    expansions.write(query+'\n')
                    
                    if self.expander:
                        # expand the query using word vectors if available
                        query = self.expander.expand(query, centroid=self.method)

                    query = self.queryparser.escape(query)
                    
                    expansions.write(query+"\n")
                    expansions.write("\n")
                    queries[elems[0]] = query

        return queries


if __name__ == "__main__":

    parser = argparse.ArgumentParser("search some lucene indexes")
    parser.add_argument("-r", "--results", nargs="?", required=False, const="results")
    parser.add_argument("-e", "--expand", nargs="?", required=False, const="expand")
    parser.add_argument("-c", "--centroid", nargs="?", required=False, const="centroid")
    parser.add_argument("-s", "--search", nargs=2)
    parser.add_argument("-d", "--dict", nargs="?", const="dict", required=False)
    args = parser.parse_args()

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    if args.results:
        if args.expand:
            from Embeddings import GoogleNewsEmbeddings
            expander = GoogleNewsEmbeddings()


        for analyzer in ['baseline', 'better']:
            for similarity in ['classic', 'bm25']:
                for requete in ['Courtes', 'Longues']:

                    if args.expand:
                        search = Search(analyzer+"_"+similarity, requete, expander=expander, method=args.centroid)
                    else:
                        search = Search(analyzer+"_"+similarity, requete)

                    print("Compiling search results for model: \n%s analyzer | %s similarity | requetes %s" % (analyzer, similarity, requete ) )
                    search.expansions_to_file()
                    search.to_file()
                    
                    
                    print("Done\n")

    elif args.search:

        search = Search(args.search[0]+"_"+args.search[1], "requetesCourtes.txt")

        if args.dict:
            print("saving a file of all words in the lucene index...")
            search.list_all_words(to_file=True)
            print("Done")
        
        print("Searching within AP88-90 corpus with Lucene model: \n%s analyzer | %s similarity" % (args.search[0], args.search[1]))

        while True:
            search_text = input("Search query: ")
            if not search_text:
                break
            search.simple_search(search_text)
        
        print("Thank you for searching, have a nice day")

    else:
        parser.print_help()
