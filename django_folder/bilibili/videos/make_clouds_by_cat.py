from . import bilibiliclass


import traceback
import sys
import csv
import os
import bleach

from functools import reduce
from operator import and_

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')
COLUMN_NAMES = dict(
    video_title ='Video Title',
    sub_cat = 'Sub-category',
    v_url = 'url',
    similar_score = 'Similar Score',
)

DF_LIST = ['Animee', 'DailyLife', 'Dance', 'Domestic', 'Entertainment',
           'Fashion', 'Games', 'Kichiku', 'Movies', 'Music', 'Science' ]

TRANSLATION = {'Animee': '动画', 'DailyLife': '生活', 'Dance': '舞蹈', 'Domestic': '国创相关',
               'Entertainment': '娱乐',
           'Fashion': '时尚', 'Games': '游戏', 'Kichiku': '鬼畜', 'Movies': '影视', 'Music': '音乐',
               'Science': '科技'}
#1
ANIMEE_PATH = {}

ANIMEE_PATH['Animee'] = 'Data/BLDataAnimee.txt'

bilibili_animee = bilibiliclass.Bilibili(cat_path_dict = ANIMEE_PATH)

bilibili_animee.load_emoticons('Data/emoticons.txt')

bilibili_animee.load_stopwords('Data/ChineseStopwords.txt')

bilibili_animee.load_D2V_model('Animee_model', os.path.abspath('videos/D2VAnimee'))

bilibili_animee.generate_wordcloud(main_category = '动画', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_animee')
#2
DANCE_PATH = {}

DANCE_PATH['Dance'] = 'Data/BLDataDance.txt'

bilibili_dance = bilibiliclass.Bilibili(cat_path_dict = DANCE_PATH)

bilibili_dance.load_emoticons('Data/emoticons.txt')

bilibili_dance.load_stopwords('Data/ChineseStopwords.txt')

bilibili_dance.smart_cut_corpus()

bilibili_dance.generate_D2V_model('Dance_model', 500)

bilibili_dance.finish_training_D2V_model('Dance_model')

bilibili_dance.save_D2V_model('D2VDance', 'Dance_model')

bilibili_dance.generate_wordcloud(main_category = '舞蹈', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_dance')
#3
DLIFE_PATH = {}

DLIFE_PATH['DailyLife'] = 'Data/BLDataDailyLife.txt'

bilibili_dlife = bilibiliclass.Bilibili(cat_path_dict = DLIFE_PATH)

bilibili_dlife.load_emoticons('Data/emoticons.txt')

bilibili_dlife.load_stopwords('Data/ChineseStopwords.txt')

bilibili_dlife.smart_cut_corpus()

bilibili_dlife.generate_D2V_model('dlife_model', 500)

bilibili_dlife.finish_training_D2V_model('dlife_model')

bilibili_dlife.save_D2V_model('D2Vdlife', 'dlife_model')


bilibili_dlife.generate_wordcloud(main_category = '生活', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_dlife')
#4
DOM_PATH = {}

DOM_PATH['Domestic'] = 'Data/BLDataDomestic.txt'

bilibili_domestic = bilibiliclass.Bilibili(cat_path_dict = DOM_PATH)

bilibili_domestic.load_emoticons('Data/emoticons.txt')

bilibili_domestic.load_stopwords('Data/ChineseStopwords.txt')

bilibili_domestic.smart_cut_corpus()

bilibili_domestic.generate_D2V_model('domestic_model', 500)

bilibili_domestic.finish_training_D2V_model('domestic_model')

bilibili_domestic.save_D2V_model('D2Vdomestic', 'domestic_model')

bilibili_domestic.generate_wordcloud(main_category = '国创相关', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_domestic')
#5
ENT_PATH = {}

ENT_PATH['Entertainment'] = 'Data/BLDataEntertainment.txt'

bilibili_entertainment = bilibiliclass.Bilibili(cat_path_dict = ENT_PATH)

bilibili_entertainment.load_emoticons('Data/emoticons.txt')

bilibili_entertainment.load_stopwords('Data/ChineseStopwords.txt')

bilibili_entertainment.smart_cut_corpus()

bilibili_entertainment.generate_D2V_model('entertainment_model', 500)

bilibili_entertainment.finish_training_D2V_model('entertainment_model')

bilibili_entertainment.save_D2V_model('D2Ventertainment', 'entertainment_model')

bilibili_entertainment.generate_wordcloud(main_category = '娱乐', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_entertainment')

#6
FASH_PATH = {}

FASH_PATH['Fashion'] = 'Data/BLDataFashion.txt'

bilibili_fashion = bilibiliclass.Bilibili(cat_path_dict = FASH_PATH)

bilibili_fashion.load_emoticons('Data/emoticons.txt')

bilibili_fashion.load_stopwords('Data/ChineseStopwords.txt')

bilibili_fashion.smart_cut_corpus()

bilibili_fashion.generate_D2V_model('fashion_model', 500)

bilibili_fashion.finish_training_D2V_model('fashion_model')

bilibili_fashion.save_D2V_model('D2Vfashion', 'fashion_model')

bilibili_fashion.generate_wordcloud(main_category = '时尚', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_fashion')

#7
G_PATH = {}

G_PATH['Games'] = 'Data/BLDataGames.txt'

bilibili_games = bilibiliclass.Bilibili(cat_path_dict = G_PATH)

bilibili_games.load_emoticons('Data/emoticons.txt')

bilibili_games.load_stopwords('Data/ChineseStopwords.txt')

bilibili_games.smart_cut_corpus()

bilibili_games.generate_D2V_model('games_model', 500)

bilibili_games.finish_training_D2V_model('games_model')

bilibili_games.save_D2V_model('D2Vgames', 'games_model')

bilibili_games.generate_wordcloud(main_category = '游戏', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_games')


#8
K_PATH = {}

K_PATH['Kichiku'] = 'Data/BLDataKichiku.txt'

bilibili_kichiku = bilibiliclass.Bilibili(cat_path_dict = K_PATH)

bilibili_kichiku.load_emoticons('Data/emoticons.txt')

bilibili_kichiku.load_stopwords('Data/ChineseStopwords.txt')

bilibili_kichiku.smart_cut_corpus()

bilibili_kichiku.generate_D2V_model('kichiku_model', 500)

bilibili_kichiku.finish_training_D2V_model('kichiku_model')

bilibili_kichiku.save_D2V_model('D2Vkichiku', 'kichiku_model')

bilibili_kichiku.generate_wordcloud(main_category = '鬼畜', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_kichiku')


#9
MOVIE_PATH = {}

MOVIE_PATH['Movie'] = 'Data/BLDataMovie.txt'

bilibili_movie = bilibiliclass.Bilibili(cat_path_dict = MOVIE_PATH)

bilibili_movie.load_emoticons('Data/emoticons.txt')

bilibili_movie.load_stopwords('Data/ChineseStopwords.txt')

bilibili_movie.smart_cut_corpus()

bilibili_movie.generate_D2V_model('movie_model', 500)

bilibili_movie.finish_training_D2V_model('movie_model')

bilibili_movie.save_D2V_model('D2Vmovie', 'movie_model')

bilibili_movie.generate_wordcloud(main_category = '影视', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_movie')


#10
MUSIC_PATH = {}

MUSIC_PATH['Music'] = 'Data/BLDataMusic.txt'

bilibili_music = bilibiliclass.Bilibili(cat_path_dict = MUSIC_PATH)

bilibili_music.load_emoticons('Data/emoticons.txt')

bilibili_music.load_stopwords('Data/ChineseStopwords.txt')

bilibili_music.smart_cut_corpus()

bilibili_music.generate_D2V_model('music_model', 500)

bilibili_music.finish_training_D2V_model('music_model')

bilibili_music.save_D2V_model('D2Vmusic', 'music_model')

bilibili_music.generate_wordcloud(main_category = '音乐', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_music')

#11
SCI_PATH = {}

SCI_PATH['Science'] = 'Data/BLDataScience.txt'

bilibili_science = bilibiliclass.Bilibili(cat_path_dict = SCI_PATH)

bilibili_science.load_emoticons('Data/emoticons.txt')

bilibili_science.load_stopwords('Data/ChineseStopwords.txt')

bilibili_science.smart_cut_corpus()

bilibili_science.generate_D2V_model('science_model', 500)

bilibili_science.finish_training_D2V_model('science_model')

bilibili_science.save_D2V_model('D2Vscience', 'science_model')

bilibili_science.generate_wordcloud(main_category = '科技', font_path = 'Data/simhei.ttf',
                                  savefig = True, figname = 'wordcloud_science')
