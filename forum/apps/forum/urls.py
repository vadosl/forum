from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from apps.forum import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.main, name='main'),
    url(r'^forum/(\d+)/$', views.forum, name='forum'),
    url(r"^thread/(\d+)/$", views.thread, name='thread'),
    url(r"^post/(new_thread|reply)/(\d+)/$", views.post, name='post'),
    url(r"^reply/(\d+)/$", views.reply, name='reply'),
    url(r"^new_thread/(\d+)/$", views.new_thread, name='new_thread'),
    url(r"^profile/(\d+)/$", views.profile, name="profile"),
)
