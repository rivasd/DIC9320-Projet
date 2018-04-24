import lucene
from org.apache.pylucene.analysis import PythonAnalyzer
from  org.apache.lucene.analysis.core import SimpleAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer

BaselineAnalyzer = SimpleAnalyzer
BetterAnalyzer = EnglishAnalyzer
