#Used views.py from pa3 ui folder, and modified by Fangfang Wan and Yilun Dai.
from django.http import HttpResponse
from django.template import loader
from . import bilibiliclass


import traceback
import sys
import csv
import os
import jieba

from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms

jieba.load_userdict("BilibiliWords.txt")
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

CAT_PATH = {}
for cat in DF_LIST:

    path = 'Data/BLData{}.txt'.format(cat)

    CAT_PATH[cat] = path

bilibili233 = bilibiliclass.Bilibili(cat_path_dict = CAT_PATH)
bilibili233.load_emoticons('Data/emoticons.txt')
bilibili233.load_stopwords('Data/ChineseStopwords.txt')
bilibili233.load_D2V_model('BLmodel', os.path.abspath('videos/D2Vmodel233'))


def _valid_result(res):
    """Validate results returned by find_courses."""
    (HEADER, RESULTS) = [0, 1]
    ok = (isinstance(res, (tuple, list)) and
          len(res) == 2 and
          isinstance(res[HEADER], (tuple, list)) and
          isinstance(res[RESULTS], (tuple, list)))
    if not ok:
        return False

    n = len(res[HEADER])

    def _valid_row(row):
        return isinstance(row, (tuple, list)) and len(row) == n
    return reduce(and_, (_valid_row(x) for x in res[RESULTS]), True)




def _load_column(filename, col=0):
    """Load single column from csv file."""
    with open(filename) as f:
        col = list(zip(*csv.reader(f)))[0]
        return list(col)


def _load_res_column(filename, col=0):
    """Load column from resource directory."""
    return _load_column(os.path.join(RES_DIR, filename), col=col)


def _build_dropdown(options):
    """Convert a list to (value, caption) tuples."""
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]


CATS = _build_dropdown([None] + _load_res_column('cat_list.csv'))


class SearchForm(forms.Form):
    video_title = forms.CharField(
        label = 'Search similar videos by video title',
        help_text = 'e.g. 【五五开】在下挂逼，有何贵干',
        required = False)

    key_words = forms.CharField(
        label = 'Search most related videos by key words',
        help_text = 'e.g. 火钳留名 老铁 厉害了',
        required = False
    )

    category = forms.ChoiceField(label = 'Category Word Cloud', choices = CATS, required = False)

def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            video_title = form.cleaned_data['video_title']
            category = form.cleaned_data['category']
            key_words = form.cleaned_data['key_words']
            if [video_title, category, key_words].count('') < 2:
                context['error'] = 'Please enter only one searching criterion.'
            elif category:
                for cat in DF_LIST:
                    if category == cat:
                        context[category] = category
            elif video_title:
                try:
                    out_df = bilibili233.topk_similar_videos(video_title, 'BLmodel', topk=10)
                    res = (out_df.columns.values.tolist(), out_df.values.tolist())
                    columns, result = res

                    # Wrap in tuple if result is not already
                    if result and isinstance(result[0], str):
                        result = [(r,) for r in result]
                    title_lst = []
                    category_lst = []
                    url_lst = []
                    similarity_lst = []
                    for row in result:
                        title_lst.append(row[0])
                        category_lst.append(row[1])
                        url_lst.append(row[2])
                        similarity_lst.append(row[3])
                    for i in range(0, 9):
                        context['title{}'.format(i)] = title_lst[i]
                        context['category{}'.format(i)] = category_lst[i]
                        context['url{}'.format(i)] = url_lst[i]

                        context['sim{}'.format(i)] = similarity_lst[i]

                    context['result'] = result
                    context['num_results'] = len(result)
                    context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]

                except KeyError:
                    context['error_key'] = 'Please enter a video name in the database.'


            elif key_words:

                out_df = bilibili233.topk_similar_videos_by_keywords(key_words, 'BLmodel', topk=10)

                res = (out_df.columns.values.tolist(), out_df.values.tolist())

                columns, result = res

                # Wrap in tuple if result is not already

                if result and isinstance(result[0], str):
                    result = [(r,) for r in result]
                title_lst = []
                category_lst = []
                url_lst = []
                similarity_lst = []
                for row in result:
                    title_lst.append(row[0])
                    category_lst.append(row[1])
                    url_lst.append(row[2])
                    similarity_lst.append(row[3])
                for i in range(0, 9):
                    context['title{}'.format(i)] = title_lst[i]
                    context['category{}'.format(i)] = category_lst[i]
                    context['url{}'.format(i)] = url_lst[i]

                    context['sim{}'.format(i)] = similarity_lst[i]
                context['result'] = result

                context['num_results'] = len(result)

                context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]
            else:
                context['error_empty'] = 'Please enter your searching criterion.'

    else:
        form = SearchForm()
    context['form'] = form
    return render(request, 'test2.html', context)

def hyper_link(request):
    return HttpResponse(request)



