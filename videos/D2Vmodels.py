import sqlite3
import os
import pandas as pd
import gensim
import sklearn
import sklearn.metrics
import jieba
import wordcloud
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as mfm


MODELS = {}
DF_LIST = ['All', 'Animee', 'DailyLife', 'Dance', 'Domestic', 'Entertainment',
           'Fashion', 'Games', 'Kichiku', 'Movies', 'Music', 'Science' ]




def generate_D2V_model(self, model_name, size):
    """
    Generate a D2V model of specified size
    """
    taggedDocs = []
    for index, row in self.dataframe.iterrows():
        docKeywords = []  # s for s in keywords if s in row['normalized_words']
        docKeywords.append(row['video_title'])
        docKeywords.append(row['category'])
        taggedDocs.append(gensim.models.doc2vec.LabeledSentence(words=row['normalized_words'], tags=docKeywords))
    D2Vmodel = gensim.models.doc2vec.Doc2Vec(taggedDocs, size=size)
    self.D2Vmodels[model_name] = D2Vmodel

def save_D2V_model(self, fname, model_name):
    """
    Save D2V model for later use
    """
    self.D2Vmodels[model_name].save(fname)

def finish_training_D2V_model(self, model_name):
    """
    Finish training a model (=no more updates, only querying) to trim unneeded model memory.
     """
    self.D2Vmodels[model_name].delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)

def avail_D2V_model(self):
    """
     Return a list of currently available D2V models
    """
    return self.D2Vmodels.keys()

def load_D2V_model(self, model_name, fname):
    """
    Load saved D2V model
    """
    D2Vmodel = gensim.models.doc2vec.Doc2Vec.load(fname)
    self.D2Vmodels[model_name] = D2Vmodel


def topk_similar_videos(self, video_name, model_name, topk=10):
    """
    find top k similar
    """
    output = []
    D2Vmodel = self.D2Vmodels[model_name]
    for index, row in self.dataframe.iterrows():
        v = row['video_title']
        url = row['video_url']
        cat = row['main category'] + "/" + row['sub category']
        tagVec = D2Vmodel.docvecs[v].reshape(1, -1)
        sim_score = sklearn.metrics.pairwise.cosine_similarity(
            tagVec, D2Vmodel.docvecs[video_name].reshape(1, -1))[0][0]
        output.append((v, cat, url, sim_score))

    output.sort(key=lambda x: x[3], reverse=True)
    output = output[1:topk + 1]

    output_df = pd.DataFrame({'Video Title': [x[0] for x in output],
                                  'Category': [x[1] for x in output],
                                  'URL': [x[2] for x in output],
                                  'Similarity': [x[3] for x in output]})
    output_df = output_df[['Video Title', 'Category', 'URL', 'Similarity']]

    return output_df

def generate_wordcloud(self, main_category, sub_category=None, max_words=100, font_path=None,
                           savefig=False, figname='wordcloud'):
    if sub_category:
        tokens= self.dataframe[(self.dataframe['main category'] == main_category)
                                   &(self.dataframe['sub category'] == sub_category)]['normalized_words'].sum()
    else:
        tokens = self.dataframe[self.dataframe['main category'] == main_category]['normalized_words'].sum()

    wc = wordcloud.WordCloud(font_path=font_path,
                            background_color="white",
                            max_words=max_words,
                            width=1000, height=1000, mode='RGBA',
                            scale=.5).generate(" ".join(tokens))
    plt.imshow(wc)
    plt.axis("off")
    if savefig:
        figname = figname + ".pdf"
        plt.savefig(figname, format='pdf')
    plt.show()


for df in DF_LIST:
    cat_df = pd.read_csv('Data/BLData{}.txt'.format(df), sep='|', header=0)
    generate_D2V_model(cat_df, df, 200)
