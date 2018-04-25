import lucene
import os
import re
import argparse

from bs4 import BeautifulSoup

from Analyzers import BaselineAnalyzer, BetterAnalyzer
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.search.similarities import ClassicSimilarity, BM25Similarity






# just a simple function to output a progressbar during indexing
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

def index(analyzer="baseline", similarity="classic"):

    tag_field_type = FieldType()
    tag_field_type.setStored(True)
    tag_field_type.setTokenized(False)
    tag_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

    content_field_type  = FieldType()
    content_field_type.setStored(False)
    content_field_type.setTokenized(True)
    content_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    idx_name = analyzer.lower()+"_"+similarity.lower()

    if not os.path.exists(os.path.join("./Indexes", idx_name)):
        os.mkdir(os.path.join("./Indexes", idx_name))

    store       = SimpleFSDirectory(Paths.get(os.path.join("./Indexes", idx_name)))
    
    if analyzer=="better":
        analyzer_inst = BetterAnalyzer()
    elif analyzer=="baseline":
        analyzer_inst = BaselineAnalyzer()

    config      = IndexWriterConfig(analyzer_inst)

    if similarity.lower()=="classic":
        config.setSimilarity(ClassicSimilarity())
    elif similarity.lower()=="bm25":
        config.setSimilarity(BM25Similarity())

    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    files_to_index = os.listdir("./AP")
    length = len(files_to_index)
    print("Indexing %d files with the %s analyzer and the %s similarity metric" % (length, analyzer, similarity))

    for index, TrecFile in enumerate(files_to_index):

        with open(os.path.abspath(os.path.join("AP",TrecFile)), 'r', encoding="utf-8", errors="ignore") as docfile:

            contents    = docfile.read()
            xml         = '<ROOT>' + contents + "</ROOT>"
            root        = BeautifulSoup(xml, 'xml')

            printProgressBar(index, length, TrecFile+"[", "]")

            for doc in root.find_all('DOC'):
                luceneDoc   = Document()

                if doc.find('FILEID') is not None:
                    fileid        = doc.find('FILEID').text.strip()
                    luceneDoc.add(Field('fileid', fileid, tag_field_type))

                if doc.find('HEAD') is not None:
                    head        = doc.find('HEAD').text.strip()
                    luceneDoc.add(Field('head', head, tag_field_type))

                if doc.find('DOCNO') is not None:
                    doc_no      = doc.find('DOCNO').text.strip()
                    luceneDoc.add(Field('docno', doc_no, tag_field_type))

                if doc.find('DATELINE') is not None:
                    dateline      = doc.find('DATELINE').text.strip()
                    luceneDoc.add(Field('dateline', dateline, tag_field_type))

                if doc.find('FIRST') is not None:
                    first      = doc.find('FIRST').text.strip()
                    luceneDoc.add(Field('first', first, tag_field_type))

                for text_el in doc.find_all('TEXT'):
                    text        = text_el.text.strip()
                    luceneDoc.add(Field('text', text, content_field_type))

                writer.addDocument(luceneDoc)
    writer.commit()

    writer.close()
    print("Done\n")

if __name__ == "__main__":

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    parser = argparse.ArgumentParser(description="Make some lucene indexes")
    parser.add_argument("-a", "--all", const="all", nargs="?", required=False)
    parser.add_argument("indextype", type=str, default="baseline", nargs='?')
    parser.add_argument('similarity', type=str, default="classic", nargs='?')

    args = parser.parse_args()

    if(args.all):
        for analyzer in ['baseline', 'better']:
            for sim in ['classic', 'bm25']:
                index(analyzer, sim)
                print("Done\n")
    else:
        index(args.indextype, args.similarity)