import lucene
import os
import re
import xml.etree.ElementTree as ET
from Analyzers import BaselineAnalyzer
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.document import Document, Field, StringField, TextField
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



for TrecFile in os.listdir("./AP"):
    with open(os.path.abspath(os.path.join("AP",TrecFile)), 'r') as docfile:
        contents    = docfile.read()
        xml         = '<ROOT>' + contents + "</ROOT>"
        root        = ET.fromstring(xml)
        pass

