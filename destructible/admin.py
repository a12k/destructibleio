from django.contrib import admin
from .models import UserFile, Attachment, Contact

admin.site.register(UserFile)
admin.site.register(Attachment)
admin.site.register(Contact)