from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import nltk
import re
import os
import codecs
from sklearn import feature_extraction
from sklearn.cluster import KMeans
import mpld3
import csv
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import string
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib
matplotlib.use('Agg')

def tokenize_and_stem(text,stopwords):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    tokens = [w for w in tokens if not w in stopwords]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    #lowers = text.lower()
    #remove the punctuation using the character deletion step of translate
    #no_punctuation = lowers.translate(None,string.punctuation)
    #tokens = nltk.word_tokenize(no_punctuation)

    #tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    tokens = [w for w in tokens if not w in stopwords]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens
url = []
title_and_description = []

with open('report.csv', 'rb') as csvfile:
     reader = csv.DictReader(csvfile)
     reader.fieldname = "votes","fetch_url","title","longtext","answers","link","date","id","tags"
     for row in reader:
         url.append(row['fetch_url'])
         title_and_description.append(row['title'] + ' '+row['longtext'])
#         import pdb;pdb.set_trace() 

stemmer = SnowballStemmer("english")
totalvocab_stemmed = []
totalvocab_tokenized = []
#import pdb;pdb.set_trace()
counter = 0
d={}
for i in title_and_description:
    #allwords_stemmed = tokenize_and_stem(i,stopwords) #for each item in 'title_and_description', tokenize/stem
    #totalvocab_stemmed.extend(allwords_stemmed) #extend the 'totalvocab_stemmed' list
#    import pdb;pdb.set_trace()
#    print counter
    i = i.lower().translate(None,string.punctuation)
    allwords_tokenized = tokenize_only(i)
    d[url[counter]] = allwords_tokenized
    totalvocab_tokenized.extend(allwords_tokenized)
    counter = counter + 1
   # import pdb;pdb.set_trace()
#data_frame = pd.DataFrame(d)
#data_frame.to_csv("finals.csv", sep="\t")

#data_frame = pd.DataFrame({'tokens': totalvocab_tokenized}, index = url)


#define vectorizer parameters
tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                 min_df=0.2, stop_words='english',
                                 use_idf=True, tokenizer=tokenize_only, ngram_range=(1,3))

#import pdb;pdb.set_trace()
tfidf_matrix = tfidf_vectorizer.fit_transform(title_and_description) #fit the vectorizer to synopses

#print(tfidf_matrix.shape)
terms = tfidf_vectorizer.get_feature_names()

dist = 1 - cosine_similarity(tfidf_matrix)
num_clusters = 5
km = KMeans(n_clusters=num_clusters)
km.fit(tfidf_matrix)
clusters = km.labels_.tolist()
#print clusters
data_frame = pd.DataFrame({'cluster': clusters}, index = url)
data_frame.to_csv("kmeans.csv", sep="\t")

from scipy.cluster.hierarchy import ward, dendrogram

linkage_matrix = ward(dist) #define the linkage_matrix using ward clustering pre-computed distances

#import pdb;pdb.set_trace();
fig, ax = plt.subplots(figsize=(15, 20)) # set size
ax = dendrogram(linkage_matrix, orientation="right", labels=url);

plt.tick_params(\
    axis= 'x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='off')

plt.tight_layout() #show plot with tight layout

#uncomment below to save figure
plt.savefig('ward_clusters.png', dpi=200) 
