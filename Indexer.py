import lucene
import os
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from Analyzers import BaselineAnalyzer, BetterAnalyzer
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
import org.apache.pylucene

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

tag_field_type = FieldType()
tag_field_type.setStored(True)
tag_field_type.setTokenized(False)
tag_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

content_field_type  = FieldType()
content_field_type.setStored(True)
content_field_type.setTokenized(True)
content_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

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

def index(name, analyzer):

    if not os.path.exists(os.path.join("./Indexes", name)):
        os.mkdir(os.path.join("./Indexes", name))

    store       = SimpleFSDirectory(Paths.get(os.path.join("./Indexes", name)))
    analyzer    = BaselineAnalyzer()
    config      = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    files_to_index = os.listdir("./AP")
    length = len(files_to_index)
    print("Indexing %d files" % length)

    for index, TrecFile in enumerate(files_to_index):

        with open(os.path.abspath(os.path.join("AP",TrecFile)), 'r', encoding="utf-8") as docfile:
            try:
                contents    = docfile.read()
            except UnicodeDecodeError:
                pass
            xml         = '<ROOT>' + contents + "</ROOT>"
            root        = BeautifulSoup(xml, 'lxml')

            printProgressBar(index, length, TrecFile+"[", "]")

            for doc in root.find_all('doc'):
                luceneDoc   = Document()

                if doc.find('fileid') is not None:
                    fileid        = doc.find('fileid').text.strip()
                    luceneDoc.add(Field('fileid', fileid, tag_field_type))

                if doc.find('head') is not None:
                    head        = doc.find('head').text.strip()
                    luceneDoc.add(Field('head', head, tag_field_type))

                if doc.find('docno') is not None:
                    doc_no      = doc.find('docno').text.strip()
                    luceneDoc.add(Field('docno', doc_no, tag_field_type))

                if doc.find('dateline') is not None:
                    dateline      = doc.find('dateline').text.strip()
                    luceneDoc.add(Field('dateline', dateline, tag_field_type))

                if doc.find('first') is not None:
                    first      = doc.find('first').text.strip()
                    luceneDoc.add(Field('first', first, tag_field_type))

                for text_el in doc.find_all('text'):
                    text        = text_el.text.strip()
                    luceneDoc.add(Field('text', text, content_field_type))

                

                writer.addDocument(luceneDoc)
    writer.commit()

    writer.close()

if __name__ == "__main__":

    index("Standard", BetterAnalyzer)