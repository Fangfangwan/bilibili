from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from .models import Category
import videosearch

# Create your views here.

def index(request):
	all_categories = Category.objects.all()
	template = loader.get_template('videos/inde.html')
	context = {
	    'all_categories': all_categories
	}
	return HttpResponse(template.render(context, request))

def detail(request, video_id):
	try:
		category = Category.objects.get(pk=category_id)
	except Category.DoesNotExist:
		raise Http404("Category does not exist")
	return HttpResponse('<h2>Details for video:' + str(video_id) + '</h2>')


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
        # check whether it's valid:
        if form.is_valid():

            # Convert form data to an args dictionary for find_courses

            video_title = form.cleaned_data['video_title']
            category = form.cleaned_data['category']
            if category:
                try:
                    res = videosearch.make_wordcloud(category)
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
                    context['err'] = ('Return of TopK_similar_videos has the wrong data type. '
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
                    res = videosearch.find_similar_videos(video_title)
                except Exception as e:
                    print('Exception caught')
                    bt = traceback.format_exception(*sys.exc_info()[:3])
                    context['err'] = """
                    An exception was thrown in topk_similar_videos:
                    <pre>{}
{}</pre>
                    """.format(e, '\n'.join(bt))

                    res = None
    else:
        form = SearchForm()
    context['form'] = form
    return render(request, 'index.html', context)
