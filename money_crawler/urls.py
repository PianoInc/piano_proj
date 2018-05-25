from django.conf.urls import url
from . import views

app_name = 'money_crawler'
urlpatterns = [
    url(r'^make_fav/(?P<idx>\d+)/$', views.make_fav, name='make_fav'),
    url(r'^make_nomal/(?P<idx>\d+)/$', views.make_nomal, name='make_nomal'),
    url(r'^make_invis/(?P<idx>\d+)/$', views.make_invis, name='make_invis'),
    url(r'^make_sel_fav/$', views.make_sel_fav, name='make_sel_fav'),
    url(r'^make_sel_nomal/$', views.make_sel_nomal, name='make_sel_nomal'),
    url(r'^make_sel_invis/$', views.make_sel_invis, name='make_sel_invis'),
    url(r'^make_invis_past_biz/$', views.invis_past_biz, name='invis_past_biz'),
    url(r'^show_vis_list/$', views.show_vis_list, name='show_vis_list'),
    url(r'^show_fav_list/$', views.show_fav_list, name='show_fav_list'),
    url(r'^show_sort_list/(?P<sort>\w+)$', views.show_sort_list, name='show_sort_list'),
    url(r'^show_invis_list/$', views.show_invis_list, name='show_invis_list'),
]

