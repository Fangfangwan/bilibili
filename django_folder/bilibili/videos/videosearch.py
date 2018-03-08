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




bilibili233 = bilibiliclass.Bilibili(cat_path_dict = CAT_PATH)
bilibili233.load_emoticons('Data/emoticons.txt')
bilibili233.load_stopwords('Data/ChineseStopwords.txt')
bilibili233.smart_cut_corpus()
bilibili233.load_D2V_model('BLmodel', 'D2Vmodel233')


def find_similar_videos(v_title):
    output_df = bilibili233.topk_similar_videos(v_title, 'BLmodel')
    return output_df

def make_wordcloud(main_category):
    bilibili233.generate_wordcloud(main_category)


