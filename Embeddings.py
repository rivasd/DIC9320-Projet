from gensim import models
from gensim.similarities.index import AnnoyIndexer
from annoy import AnnoyIndex

import lucene
import os

from Search import Search

GOOGLENEWS_VECTORS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "GoogleNews-vectors-negative300.bin")
annoy_dir = os.path.join(os.path.dirname(__file__), "annoy")

def build_annoy_from_lucene(analyzer="baseline", similarity="classic"):

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    model       = models.KeyedVectors.load_word2vec_format(GOOGLENEWS_VECTORS_PATH, binary=True)
    annoy_index = AnnoyIndex(300)
    lucene_idx  = Search(analyzer+"_"+similarity, "requetesCourtes.txt")
    vocab       = lucene_idx.list_all_words()

    for idx, word in enumerate(vocab):
        try:
            word_vector = model.wv[word]
            annoy_index.add_item(idx, word_vector)
        except KeyError:
            print("weird word %s was not among the loaded embeddings" % (word,))
    
    annoy_index.build(10)

    if not os.path.isdir(annoy_dir):
        os.mkdir(annoy_dir)

    annoy_index.save("./annoy/%s_%s_wordvecs.ann" %(analyzer, similarity))



class Embeddings(object):

    def __init__(self, modelpath="", is_bin=False):

        if modelpath:
            self.load_vectors(modelpath, is_bin)
        

    def load_vectors(self, modelpath, is_bin=False):
        print("Initializing Embeddings")
        model = models.KeyedVectors.load_word2vec_format(modelpath, binary=is_bin)
        print("word vectors successfully loaded in memory")
        print("Now building ANNOY index...")
        
        # self.indexer = AnnoyIndexer(model, 10)
        self.model = model
        print("Done\n")

    # def find_most_similar(self, word_list, n):
    #     return self.model.most_similar(positive=word_list, topn=n, indexer=self.indexer)


class GoogleNewsEmbeddings(Embeddings):

    def __init__(self):
        super(GoogleNewsEmbeddings, self).__init__(GOOGLENEWS_VECTORS_PATH, is_bin=True)