from django.conf.urls import url
from . import views

app_name = 'appstore_crawler'
urlpatterns = [
    url(r'^show_list/$', views.show_app_list, name='show_list'),
    url(r'^show_list/detail/(?P<app_id>\d+)/$', views.show_detail, name='show_detail'),
    url(r'^show_icon/$', views.show_app_icon, name='show_icon'),
    url(r'^show_img/$', views.show_app_img, name='show_img'),
    url(r'^show_review/$', views.show_app_review, name='show_review'),
]
