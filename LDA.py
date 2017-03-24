'''
Created on Dec 28, 2016

@author: Rob

Some code borrowed from http://scikit-learn.org/stable/auto_examples/applications/topics_extraction_with_nmf_lda.html#sphx-glr-auto-examples-applications-topics-extraction-with-nmf-lda-py
'''
# module usage instructions: https://github.com/smilli/py-corenlp/blob/master/README.md#usage
from pycorenlp import StanfordCoreNLP

# CMD commands to open CoreNLP server connection
# cd C:\Users\Rob\Desktop\CoreNLP\stanford-corenlp-full-2016-10-31
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer [port] [timeout]

import os, re, codecs, math
import csv

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups
from cookielib import DAYS

n_samples = 32567  # manually confirmed number of docs
n_features = 1000000 # possible words, set arbitrarily high
n_top_words = 25  # words per topic

# For reporting and debugging the topic output
def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()

# Returns the number of days since the first article given a string representing a date
# in the format dd/mm/yyyy
def days_since_start(date_str):
  # first article is 1/1/1987 about Iran-Contra affair
  nums = date_str.split("/")
  acc = 0
  month = int(nums[0])
  days = int(nums[1])
  year = int(nums[2])
  if month > 1:
    acc += sum(days_of_month[1:month])
  acc += days
  if year > 1987:
    years = float(year - 1987)
    leaps = int(math.floor(years / 4.0))
    acc += (365*years) + leaps
  return(acc)

years = range(1987, 2008)
months = range(1, 13)
days_of_month = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Change these to the directory of the corpus you wish to analyze with LDA
irandir = r'C:\Users\Rob\Desktop\Perry Thesis\nyt_corpus_LDC2008T19\nyt_corpus\iranarticlesNoNum' + "\\"
topicdir = r'C:\Users\Rob\Desktop\Perry Thesis\nyt_corpus_LDC2008T19\nyt_corpus\topicwords' + "\\"
datadir = r'C:\Users\Rob\Desktop\Perry Thesis\nyt_corpus_LDC2008T19\nyt_corpus\topicdistributions' + "\\"

print("Loading dataset...")
file_endings_list = os.listdir(irandir)
iran_articles_list = []
for ending in file_endings_list:
  iran_articles_list.append(str(irandir + ending))

iran_text_list = []  
article_dates_list = []
for f in iran_articles_list:
  try:
    tfile = open(f, "r")
    article_text = ""
    tfile.readline()
    next_line = tfile.readline()
    article_date = re.sub('\n', '', next_line)
    article_dates_list.append(article_date)
    while(next_line != ""):
      next_line = tfile.readline()
      article_text = article_text + next_line
    iran_text_list.append(article_text)
  finally:
    tfile.close()

# write dates to a csv file for later data analysis
outcsv = datadir + "timevar.csv"
with open(outcsv, "wb") as csvfile:
  writer = csv.writer(csvfile, delimiter=',', quotechar='|', 
                      quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
  for date in article_dates_list:
    row_list = []
    row_list.append(days_since_start(date))
    writer.writerow(row_list)
  
# Use tf (raw term count) features for LDA.
print("Extracting tf features for LDA...")
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=1,
                                max_features=n_features,
                                stop_words='english')
tf = tf_vectorizer.fit_transform(raw_documents= iran_text_list) # Document-Word Matrix
feature_names = tf_vectorizer.get_feature_names()

print("Fitting LDA models with tf features, "
      "n_samples=%d and n_features=%d..."
      % (n_samples, n_features))

for k in range(20, 21):
  print("Fitting model for k = ", k)
  lda = LatentDirichletAllocation(n_topics=k, max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0)
  lda.fit(tf)
  
  filename = topicdir + "k" + str(k) + ".txt"
  try:
    topicfile = open(filename, "w")
    for topic_idx, topic in enumerate(lda.components_):
        k_prefix = "Topic " + str(topic_idx + 1) + ": "
        topics_suffix = " ".join([feature_names[i]
                                  for i in topic.argsort()[:-n_top_words - 1:-1]])
        topicfile.write(codecs.encode(k_prefix + topics_suffix))
        topicfile.write('\n')
  finally:
    topicfile.close()
  
  topic_dist = lda.transform(tf)
  
  csvname = datadir + "k" + str(k) + ".csv"
  with open(csvname, "wb") as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', 
                        quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    writer.writerows(topic_dist)

#print("\nTopics in LDA model:")
#tf_feature_names = tf_vectorizer.get_feature_names()
#print_top_words(lda, tf_feature_names, n_top_words)

###################################
############ NOT USED #############
###################################

# Use tf-idf features for NMF.
#print("Extracting tf-idf features for NMF...")
#tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
#                                   max_features=n_features,
#                                   stop_words='english')
#tfidf = tfidf_vectorizer.fit_transform(iran_articles_list)

# Fit the NMF model
#print("Fitting the NMF model with tf-idf features, "
#      "n_samples=%d and n_features=%d..."
#      % (n_samples, n_features))
#nmf = NMF(n_components=n_topics, random_state=1,
#          alpha=.1, l1_ratio=.5).fit(tfidf)
#
#print("\nTopics in NMF model:")
#tfidf_feature_names = tfidf_vectorizer.get_feature_names()
#print_top_words(nmf, tfidf_feature_names, n_top_words)