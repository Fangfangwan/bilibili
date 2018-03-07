from django.conf.urls import url
from .import views
from django.urls import path

urlpatterns = [
    # /categories/
    path('', views.index, name='index'

    # /categories/category_id
    #url(r'^(?P<category_id>[0-9]+)/$', views.detail, name = 'detail'),

]
