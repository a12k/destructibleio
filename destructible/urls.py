from django.conf.urls import url
from .views import file, fileList, expire_now

urlpatterns = [
	url(r'^(?i)$', fileList, name='fileList'),
	url(r'^(?i)(?P<pk>\d+)/$', expire_now, name='expire_now'),
	url(r'^(?i)destructible/(?P<file_hash>\w+)/', file), #removing uploader stopped files from being downloaded, wtf?
]