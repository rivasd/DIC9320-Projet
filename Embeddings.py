from gensim import models
import gensim.utils
from gensim import matutils
from numpy import array, float
from gensim.similarities.index import AnnoyIndexer
from annoy import AnnoyIndex

import lucene
import os
import numpy as np
import nltk
from nltk.corpus import stopwords


from Indexer import printProgressBar

GOOGLENEWS_VECTORS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "GoogleNews-vectors-negative300.bin")
SLIM_VECTORS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "vectors", "googleNewsSlim.bin.gz")
annoy_dir = os.path.join(os.path.dirname(__file__), "vectors")

nltk_stopwords = set(stopwords.words("english"))

def filter_embeddings_with_lucene(analyzer="baseline", similarity="classic"):

    from Search import Search
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    lucene_idx  = Search(analyzer+"_"+similarity, "requetesCourtes.txt")
    vocab       = set(lucene_idx.list_all_words())
    better_lucene_idx = Search("better_bm25", "requetesCourtes.txt")
    better_vocab = set(better_lucene_idx.list_all_words())
    vocab = vocab | better_vocab

    print("Loading full GoogleNews Embeddings into memory...")
    model = models.KeyedVectors.load_word2vec_format(GOOGLENEWS_VECTORS_PATH, binary=True)
    print("Done")
    indices_to_delete = []
    j = 0
    vocab_length = len(model.index2word)

    print("now filtering the %d embeddings to keep only words in our Lucene index..." % vocab_length)
    for i,w in enumerate(model.index2word):
        l = w.strip().lower()
        found = False
        if l in vocab:
            found = True
        if found:
            model.vocab[w].index = j
            j += 1
        else:
            del model.vocab[w]
            indices_to_delete.append(i)

        printProgressBar(i+1, vocab_length)
    print("Done.")
    if not os.path.isdir(annoy_dir):
        os.mkdir(annoy_dir)
    print("deleting %d unused entries from the original model..." % len(indices_to_delete))
    model.syn0 = np.delete(model.syn0, indices_to_delete, axis=0)
    model.save_word2vec_format(annoy_dir + '/googleNewsSlim.bin.gz', binary=True)
    print("Done")
    del model



class Embeddings(object):

    def __init__(self, modelpath="", is_bin=False):

        if modelpath:
            self.load_vectors(modelpath, is_bin)
        

    def load_vectors(self, modelpath, is_bin=False):
        print("Initializing Embeddings")
        model = models.KeyedVectors.load_word2vec_format(modelpath, binary=is_bin)
        print("word vectors successfully loaded in memory")
        print("Now building ANNOY index...")
        
        self.indexer = AnnoyIndexer(model, 10)
        self.model = model
        print("Done\n")

    def find_most_similar(self, word_list, n):
        return self.model.most_similar(positive=word_list, topn=n, indexer=self.indexer)

    def expand(self, query, topn=10, centroid=None):

        known_words = []
        unknown_words   = []
        candidates = list()
        lowered_query = []

        #we need a better way to tokenize the query


        for word in nltk.word_tokenize(query):
            try:
                if word in nltk_stopwords:
                    continue
                word = word.lower()
                self.model.wv[word]
                known_words.append(self.model.word_vec(word, use_norm=True))
                candidates += self.model.most_similar(positive=word, topn=5)
                lowered_query.append(word)
            except KeyError:
                print("the following query word: %s was not in our corpus" % word)
                unknown_words.append(word)
        
        query_vec = matutils.unitvec(array(known_words).mean(axis=0)).astype(float)

        sorted(candidates, key=lambda word: self.model.distances(query_vec, [word[0]])[0] )
        if centroid == "centroid":
            candidates = self.model.similar_by_vector(query_vec, topn=50)

            bonus = " ".join([entry[0] for entry in candidates if entry[0].lower() not in lowered_query][:10])
        else:
        #execute nearest neighbors search, apparently no need for ANNOY speedup?
            bonus = " ".join([entry[0] for entry in candidates][:10])
        
        return query + " " + bonus

        



class GoogleNewsEmbeddings(Embeddings):

    def __init__(self):
        super(GoogleNewsEmbeddings, self).__init__(SLIM_VECTORS_PATH, is_bin=True)