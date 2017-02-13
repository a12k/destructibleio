# custom_storages.py
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION
	
class MediaStorage(S3BotoStorage):
	location = settings.MEDIAFILES_LOCATION
	file_overwrite = False
	
	from django.conf import settings

class MyS3Storage(S3BotoStorage):
	
	def __init__(self, *args, **kwargs):
		kwargs['bucket'] = getattr(settings, 'AWS_STATIC_BUCKET_NAME')
		super(MyS3Storage, self).__init__(*args, **kwargs)