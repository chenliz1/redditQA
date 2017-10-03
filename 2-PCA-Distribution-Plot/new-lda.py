"""
The script is created after 9.26 meeting, for fixing the issues listed at: https://github.com/chocoluffy/redditQA/issues/1.
"""

import json
from pprint import pprint
from pymongo import MongoClient
import pickle
from collections import defaultdict

subreddits = []
data = []
commentCounters = []
# counter = 0

# 898 subreddit with >100 ups comments concated, from rc-2015-06 10G data.
def load_from_file():
    with open('3-results-20170921-224241.json') as f:
        for line in f:
            obj = json.loads(line)
            subreddits.append(obj["subreddit"])
            data.append(obj["comments"])
            commentCounters.append(obj["countcomments"])

# use pymongo to load large chunk of data from mongo.
def load_from_mongo():
    # Use pymongo to achieve same effect as below codes. 
    con = MongoClient('localhost', 27017)
    db = con.test
    pipe = [
        {'$sort': {"ups": -1 }}, # sort before grouping, so that the comments array is sorted in order.
        {'$group': {'_id': '$subreddit', 'comments': { '$push':  { 'body': "$body", 'ups': "$ups" } }}},
        {'$addFields': { 'commentsCount': { '$size': "$comments" } } },
        { "$project": { 
            "comments": { "$slice": [ "$comments", 100 ] }, # slice the top 100 comments.
            "commentsCount": 1
        }}
    ]

    sub_data = defaultdict(dict)
    counter = 0
    for document in db.docs_l2.aggregate(pipeline = pipe, allowDiskUse = True):
        try:
            counter += 1
            print "Processing #%d subreddit"%(counter)
            docset = " ".join(map(lambda x: x["body"], document['comments']))
            sub_data[document['_id']]['docset'] = docset
            sub_data[document['_id']]['length'] = document['commentsCount']
        except:
            continue

    pickle.dump(sub_data, open("subreddit_comments.pkl", 'wb'))


load_from_mongo()

# # compile documents

# # doc1 = "Sugar is bad to consume. My sister likes to have sugar, but not my father."
# # doc2 = "My father spends a lot of time driving my sister around to dance practice."
# # doc3 = "Doctors suggest that driving may cause increased stress and blood pressure."
# # doc4 = "Sometimes I feel pressure to perform well at school, but my father never seems to drive my sister to do better."
# # doc5 = "Health experts say that Sugar is not good for your lifestyle."

# # compile documents
# doc_complete = data

# from nltk.corpus import stopwords 
# from nltk.stem.wordnet import WordNetLemmatizer
# from gensim.models import Phrases
# import string
# stop = set(stopwords.words('english'))
# exclude = set(string.punctuation) 
# lemma = WordNetLemmatizer()

# # Remove stopwords, punctuation and normalize them.
# def clean(doc):
#     stop_free = " ".join([i for i in doc.lower().split() if i not in stop and len(i) > 1])
#     punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
#     normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
#     return normalized

# doc_clean = [clean(doc).split() for doc in doc_complete] 

# # Add bigrams that appear 20 times or more.
# bigram = Phrases(doc_clean, min_count=20)
# for idx in range(len(doc_clean)):
#     for token in bigram[doc_clean[idx]]: 
#         if '_' in token:
#             doc_clean[idx].append(token)

# # pprint(doc_clean)

# import gensim
# from gensim import corpora
# import os.path

# # If dictionary model exists, use it; Otherwise, save a new one.
# if not os.path.exists('models/2/new-rc-lda.dict'):
#     # Creating the term dictionary of our courpus, where every unique term is assigned an index. 
#     dictionary = corpora.Dictionary(doc_clean)
#     # Filter out words that occur less than 20 documents, or more than 50% of the documents.
#     dictionary.filter_extremes(no_below=20, no_above=0.5)
#     dictionary.save('models/2/new-rc-lda.dict')
# else:
#     dictionary = corpora.Dictionary.load('models/2/new-rc-lda.dict')


# if not os.path.exists('models/2/new-doc-term.mm'):
#     # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above. [Bag Of Word]
#     doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
#     # Save the matrix into Market Matrix format. 
#     corpora.MmCorpus.serialize('models/2/new-doc-term.mm', doc_term_matrix)
# else:
#     doc_term_matrix = corpora.MmCorpus('models/2/new-doc-term.mm')


# # pprint(doc_term_matrix)

# import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# # Save LDA model
# if not os.path.exists('models/2/new-model.lda'):
#     # Creating the object for LDA model using gensim library
#     Lda = gensim.models.ldamodel.LdaModel
#     # Running and Trainign LDA model on the document term matrix.
#     ldamodel = Lda(doc_term_matrix, num_topics=100, id2word = dictionary, passes=50)
#     ldamodel.save('models/2/new-model.lda')
# else:
#     ldamodel = gensim.models.ldamodel.LdaModel.load('models/2/new-model.lda')


# # Return all topics probability distribution for each document, instead of clipping value using threshold.
# def get_doc_topics(lda, bow):
#     gamma, _ = lda.inference([bow])
#     topic_dist = gamma[0] / sum(gamma[0])
#     # return [(topic_id, topic_value) for topic_id, topic_value in enumerate(topic_dist)]
#     return topic_dist # return direct value


# # Covert the comments from data into a topic vector, for now given 100 topics, each vector will be 
# # of length 100, indicating the probability from each topic.
# rc_tvec = []
# for doc_term_vec in doc_term_matrix:
#     topic_dist = get_doc_topics(ldamodel, doc_term_vec)
#     rc_tvec.append(topic_dist)
#     # topic_dist = ldamodel[doc_term_vec] # Bad, only shows top several topics; it clips the topic value under threshold.
    


# # Below are tasks utilizing the above model.


# # pprint(rc_tvec)
# # Print the topic-words distribution for some specific topics.
# import operator
# def print_specific_subreddit_topic():    
#     dominant_counter = 0
#     for label, topic_dist_vec in zip(subreddits, rc_tvec):
#         index, value = max(enumerate(topic_dist_vec), key=operator.itemgetter(1))
#         if label in ["apple", "anime", "sports", "nba", "4chan", "PS4", "technology", "Music"]:
#             print "For subreddit: ", label, " , the dominant topic is: ", index, " with prob: ", value, ldamodel.show_topic(index, topn=20)
#         if value > 0.5:
#             dominant_counter += 1
#     print "From ", len(subreddits), " all subreddit, ", dominant_counter, " of all owns a dominant topics"

# def print_general_subreddit_topic():
#     ldamodel.print_topics(20)


# print_general_subreddit_topic()


# # Clean the matrix; And slice with the fist 50 non empty subreddit.
# from sklearn.manifold import TSNE
# import matplotlib.pyplot as plt
# import matplotlib.cm as cm
# import numpy as np
# from adjustText import adjust_text
# import math
# def plot():
#     counter = 0
#     new_labels = []
#     new_rc_tvec = []
#     new_comment_counter = []
#     for label, t_dist, cc in zip(subreddits, rc_tvec, commentCounters):
#         if len(t_dist) == 0:
#             continue
#         else:
#             counter += 1
#             if counter < 500:
#                 new_labels.append(label)
#                 new_rc_tvec.append(t_dist)
#                 new_comment_counter.append(cc)





#     colors = cm.rainbow(np.linspace(0, 1, len(new_labels)))

#     tsne_results = TSNE(n_components=2, perplexity=40, verbose=2).fit_transform(rc_tvec)

#     def tsne_plot(labels, tokens, cc):
        
#         labels = labels
#         tokens = tokens
        
#         tsne_model = TSNE(perplexity=40, n_components=2, init='pca', n_iter=2500, random_state=23)
#         new_values = tsne_model.fit_transform(tokens)

#         x = []
#         y = []
#         for value in new_values:
#             x.append(value[0])
#             y.append(value[1])
            
#         plt.figure(figsize=(16, 16)) 
#         # fig, ax = plt.subplots() # note we must use plt.subplots, not plt.subplot

#         for i in range(len(x)):
#             sct = plt.scatter(x[i],y[i], color=colors[i], s=float(cc[i]), linewidths=2, edgecolor='w')
#             sct.set_alpha(0.75)
#             if float(cc[i]) > 30:
#                 plt.annotate(labels[i],
#                             xy=(x[i], y[i]),
#                             xytext=(5, 2),
#                             textcoords='offset points',
#                             ha='right',
#                             va='bottom')
#             # Draw cycles.
#             # cycle = plt.Circle((x[i],y[i]), math.log1p(float(cc[i])), fill=False)
#             # ax.add_artist(cycle)

#         # texts = []
#         # for m, n, p in zip(x, y, labels):
#         #     texts.append(plt.text(m, n, p))
#         # adjust_text(texts, only_move={'points':'y', 'text':'y'})

        
#         plt.show()

#     tsne_plot(new_labels, new_rc_tvec, new_comment_counter)

#     # print(subreddits)
#     # pprint(ldamodel.print_topics(num_topics=100, num_words=5))
#     # pprint(ldamodel.print_topics(num_topics=3, num_words=3))

# # plot()