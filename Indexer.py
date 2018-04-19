import lucene
import os
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from Analyzers import BaselineAnalyzer
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
import org.apache.pylucene

lucene.initVM(vmargs=['-Djava.awt.headless=true'])


if not os.path.exists("./Indexes/Baseline"):
    os.mkdir("./Indexes/Baseline")

store       = SimpleFSDirectory(Paths.get("./Indexes/Baseline"))
analyzer    = BaselineAnalyzer()
config      = IndexWriterConfig(analyzer)
config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
writer = IndexWriter(store, config)

tag_field_type = FieldType()
tag_field_type.setStored(True)
tag_field_type.setTokenized(False)
tag_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

content_field_type  = FieldType()
content_field_type.setStored(True)
content_field_type.setTokenized(True)
content_field_type.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)


for TrecFile in os.listdir("./AP"):
    with open(os.path.abspath(os.path.join("AP",TrecFile)), 'r') as docfile:
        contents    = docfile.read()
        xml         = '<ROOT>' + contents + "</ROOT>"
        root        = BeautifulSoup(xml, 'lxml')
        for doc in root.find_all('doc'):
            luceneDoc   = Document()
            
            file_id     = doc.find('fileid').text.strip()

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
