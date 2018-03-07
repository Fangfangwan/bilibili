import sqlite3
import os
import pandas as pd
import gensim
import sklearn
import sklearn.metrics
import bilibiliclass

# Use this filename for the database
DF_LIST = ['Animee', 'DailyLife', 'Dance', 'Domestic', 'Entertainment',
           'Fashion', 'Games', 'Kichiku', 'Movies', 'Music', 'Science' ]

CAT_PATH = {}
for cat in DF_LIST:

    path = 'Data/BLData{}.txt'.format(cat)

    CAT_PATH[cat] = path




bilibili666 = bilibiliclass.Bilibili(cat_path_dict = CAT_PATH)
bilibili666.load_emoticons('Data/emoticons.txt')
bilibili666.load_stopwords('Data/ChineseStopwords.txt')
bilibili666.smart_cut_corpus()
bilibili666.load_D2V_model('BLmodel', 'D2Vmodel666')
bilibili666.generate_D2V_model('BLmodel', size = 500)
bilibili666.finish_training('BLmodel')
bilibili666.save_D2V_model('D2Vmodel666', 'BLmodel')


def find_similar_videos(v_title):
    output_df = bilibili666.topk_similar_videos(v_title, 'BLmodel')
    return output_df

def make_wordcloud(main_category):
    bilibili666.generate_wordcloud(main_category)


