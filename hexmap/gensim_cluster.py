import pandas as pd
import numpy as np
import cPickle as pkl
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models import Word2Vec
import time

WORD2VEC_MODEL = '../data/word2vec_modelf'
START_DATE = '2014-12-01'
END_DATE = '2015-03-31'

class ReviewModel(object):
    """docstring for ReviewModel"""
    def __init__(self, model_file=WORD2VEC_MODEL, similarity=.65):
        self.model = Word2Vec.load(model_file)
        self.topic = {}
        self.similarity = similarity

    def closest_words(self, word):
        if word not in self.topic:
            self.topic[word] = set([item[0] for item in self.model.most_similar(word, 
                                    topn=100) if item[1]>self.similarity])
        return [word] + list(self.topic[word])

    def load_data(self, filename):
        df = pkl.load(open(filename))
        self.reviews = df.pop('text').values
        self.coords = df[['date', 'lati', 'longi']]

    def construct_counts(self):
        print 'constructing counts...'
        start = time.time()
        vect = CountVectorizer(min_df=25, max_df=.4)
        self.counts = vect.fit_transform(self.reviews)
        self.reviews = []
        self.vocabulary = vect.vocabulary_
        print '%s seconds' % (time.time()-start)

    def query(self, term):
        response = self.coords.copy()
        mask = [self.vocabulary[word] for word in self.closest_words(term) if word in self.vocabulary]
        response['flag'] = (self.counts[:, mask] > 0).astype(int).max(axis=1).toarray()
        response['name'] = term
        return response
 

if __name__ == '__main__':
    reviews_pkl = '../data/reviews%s%s.pkl' % (START_DATE, END_DATE)
    rm = ReviewModel()
    rm.load_data(reviews_pkl)
    rm.construct_counts()
    with open('../data/model.pkl', 'w') as f:
        pkl.dump(rm, f)

    print rm.query('bacon')
    