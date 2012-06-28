# vim: set fileencoding=utf-8 :
from django.conf.urls.defaults import patterns, url
from tagy import views

urlpatterns = patterns('',
    url('^$', views.TagListView.as_view(), name='tagy-tag-list'),
    url('^(?P<slug>[^/]+)/$', views.TagDetailView.as_view(), name='tagy-tag-detail'),
)
