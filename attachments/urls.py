from django.conf.urls.defaults import *
from views import add, delete, update, download, thumbnail

urlpatterns = patterns(
    '',
    url(r'^add/(?P<app_label>[\w\-]+)/(?P<module_name>[\w\-]+)/(?P<pk>\d+)/$', add, name='add'),
    url(r'^delete/(?P<pk>\d+)/$', delete, name='delete'),
    url(r'^update/(?P<pk>\d+)/$', update, name='update'),
    url(r'^download/(?P<pk>\d+)/$', download, name='download'),
    url(r'^thumbnail/(?P<attachment_pk>\d+)/(?P<width>\d+)x(?P<height>\d+)/$', thumbnail, name='thumbnail'),
)
