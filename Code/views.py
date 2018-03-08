from django.http import HttpResponse
from django.template import loader
from . import bilibiliclass


import traceback
import sys
import csv
import os

from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms


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

CAT_PATH = {}
for cat in DF_LIST:

    path = 'Data/BLData{}.txt'.format(cat)

    CAT_PATH[cat] = path

bilibili233 = bilibiliclass.Bilibili(cat_path_dict = CAT_PATH)
bilibili233.load_emoticons('Data/emoticons.txt')
bilibili233.load_stopwords('Data/ChineseStopwords.txt')
#bilibili233.smart_cut_corpus()
bilibili233.load_D2V_model('BLmodel', '/Users/yilundai/Documents/Winter2018/CS122/bilibili/videos/D2Vmodel233')


def _valid_result(res):
    """Validate results returned by find_topk."""
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


class IntegerRange(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.IntegerField())
        super(IntegerRange, self).__init__(fields=fields,
                                           *args, **kwargs)

    def compress(self, data_list):
        if data_list and (data_list[0] is None or data_list[1] is None):
            raise forms.ValidationError('Must specify both lower and upper '
                                        'bound, or leave both blank.')

        return data_list




RANGE_WIDGET = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput,
                                                  forms.widgets.NumberInput))





class SearchForm(forms.Form):
    video_title = forms.CharField(
        label = 'Search video title',
        help_text = 'e.g. 【琅琊榜】鬼畜 私炮房炸了',
        required = False)

    category = forms.ChoiceField(label = 'Category', choices = CATS, required = False)




def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        print(form)
        # check whether it's valid:
        if form.is_valid():

            # Convert form data to an args dictionary for find_courses

            video_title = form.cleaned_data['video_title']
            category = form.cleaned_data['category']
            if category:
                try:
                    res = bilibili233.generate_wordcloud(category)
                except Exception as e:
                    print('Exception caught')
                    bt = traceback.format_exception(*sys.exc_info()[:3])
                    context['err'] = """
                    An exception was thrown in generate_wordcloud:
                    <pre>{}
{}</pre>
                    """.format(e, '\n'.join(bt))

                    res = None
                # Handle different responses of res
                if res is None:
                    context['result'] = None
                elif isinstance(res, str):
                    context['result'] = None
                    context['err'] = res
                    result = None
                elif not _valid_result(res):
                    context['result'] = None
                    context['err'] = ('Return of generate wordcloud has the wrong data type. '
                                      )
                else:
                    columns, result = res[0], res[1:]

                    # Wrap in tuple if result is not already
                    if result and isinstance(result[0], str):
                        result = [(r,) for r in result]

                    context['result'] = result
                    context['num_results'] = len(result)
                    context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]
            elif video_title:
                try:
                    out_df = bilibili233.topk_similar_videos(video_title, 'BLmodel')
                    res = (out_df.columns.values.tolist(), out_df.values.tolist())
                except Exception as e:
                    print('Exception caught')
                    bt = traceback.format_exception(*sys.exc_info()[:3])
                    context['err'] = """
                    An exception was thrown in topk_similar_videos:
                    <pre>{}
{}</pre>
                    """.format(e, '\n'.join(bt))

                    res = None
                if res is None:
                    context['result'] = None
                elif isinstance(res, str):
                    context['result'] = None
                    context['err'] = res
                    result = None
                elif not _valid_result(res):
                    context['result'] = None
                    context['err'] = ('Return of TopK_similar_videos has the wrong data type. '
                                      )
                else:
                    columns, result = res

                    # Wrap in tuple if result is not already
                    if result and isinstance(result[0], str):
                        result = [(r,) for r in result]

                    context['result'] = result
                    context['num_results'] = len(result)
                    context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]
    else:
        form = SearchForm()
    context['form'] = form
    return render(request, 'index.html', context)
