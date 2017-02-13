from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from destructible.views import file, expire_now, extend_time, remove_buttons, password_required, passwordprotected, userfilelist, expire_now_console, email, moreinfo, thanks, text
admin.autodiscover()

urlpatterns = [
	url(r'^accounts/', include('registration.backends.default.urls')),
	url(r'^accounts/', include('django.contrib.auth.urls')),
	url(r'^payments/', include('djstripe.urls', namespace='djstripe')),
	url(r'^email/$',
        email,
        name='email'
        ),
    url(r'^thanks/$',
        thanks,
        name='thanks'
        ),
	url(r'^moreinfo/$',
        moreinfo,
        name='moreinfo'
        ),
	url(r'^text/$',
        text,
        name='text'
        ),
	url(r'^destructible/', include('destructible.urls')),
	url(r'^destructible/expired', TemplateView.as_view(template_name='destructible/expired.html')),
	url(r'^', include('destructible.urls')),
	url(r'^password_required/(?P<file_hash>\w+)/$', password_required, name='password_required'),
	url(r'^passwordprotected/(?P<file_hash>\w+)/$', passwordprotected, name='passwordprotected'),
	url(r'^filelist/$', userfilelist, name='userfilelist'),
	url(r'^(?P<file_hash>\w+)/$', file, name='file'),
	url(r'^extend_time/(?P<uuid>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/$', extend_time, name='extend_time'),
	url(r'^expire_now/(?P<uuid>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/$', expire_now, name='expire_now'),
	url(r'^expire_now_console/(?P<uuid>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/$', expire_now_console, name='expire_now_console'),
	url(r'^remove_buttons/(?P<uuid>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/$', remove_buttons, name='remove_buttons'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)