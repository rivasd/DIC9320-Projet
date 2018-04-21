import lucene
from org.apache.pylucene.analysis import PythonAnalyzer
from  org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer

BaselineAnalyzer = SimpleAnalyzer
BetterAnalyzer = StandardAnalyzer