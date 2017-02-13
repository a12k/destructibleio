import datetime, random
from datetime import timezone
from urllib.request import urlopen

import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect

from .models import UserFile, Attachment, Contact
from .forms import UserFileForm, ContactForm, UploadForm, NoAuthUploadForm, ActiveUploadForm, ActiveUserFileForm, NoAuthUserFileForm

from djstripe.utils import subscriber_has_active_subscription
from djstripe.decorators import subscription_payment_required

#for taking text input instead of a file
def text(request):

	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	if request.method == 'POST':
		fform = NoAuthUserFileForm(request.POST) #unregistered user
		nform = NoAuthUploadForm(request.POST, request.FILES) #smaller file size, one file only
			
		if fform.is_valid() and nform.is_valid():

			f = UserFile() 
			file_hash = human_readable_hash()
		
			f.hash = file_hash
			f.expire = fform.cleaned_data['expire']
			f.max_expire = 65
			f.save()
			
			docfile = Attachment(docfile = request.FILES['docfile'], userfile=f).save()
			
		return redirect('destructible.views.file', file_hash=f.hash)	
		
	else:
		aform = ActiveUploadForm()
		eform = ActiveUserFileForm()
	return render(request, "destructible/text.html", {'is_active': is_active})
	
def fileList(request):
	
	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
	
	def human_readable_hash():
		adj = open(os.path.join(settings.PROJECT_ROOT, 'adjlist.txt'))
		noun = open(os.path.join(settings.PROJECT_ROOT, 'nounlist.txt'))
		adjwords = [line.strip() for line in adj]
		nounwords = [line.strip() for line in noun]
		return ''.join(random.choice(adjwords) + random.choice(adjwords) + random.choice(nounwords))
	contactform = ContactForm(request.POST)
	c = Contact()
	
	if is_active:
		if request.method == 'POST':
			eform = ActiveUserFileForm(request.POST) #paid user
			aform = ActiveUploadForm(request.POST, request.FILES)
			
			if eform.is_valid() and aform.is_valid():

				f = UserFile() 
				file_hash = human_readable_hash()

				if eform.data['hash']:
					f.hash = eform.data['hash']
				else:
					f.hash = file_hash
						
				f.expire = eform.cleaned_data['expire']
				f.max_expire = 1440
				f.password = eform.cleaned_data['password']
				f.user_name = request.user.username
				f.save()
					
				for afile in request.FILES.getlist('docfile'):
					Attachment(docfile=afile, userfile=f).save()
					
				return redirect('destructible.views.file', file_hash=f.hash)

		else:
			aform = ActiveUploadForm()
			eform = ActiveUserFileForm()
			
		return render(request, 'destructible/file.html', {'eform': eform, 'aform': aform, 'is_active': is_active})

	elif request.user.is_authenticated():
		if request.method == 'POST':
			form = UserFileForm(request.POST) #registered, not paid
			uform = UploadForm(request.POST, request.FILES) #auth/active user form, multi files
			
			if form.is_valid() and uform.is_valid():

				f = UserFile() 
				file_hash = human_readable_hash()
		
				if form.data['hash']:
					f.hash = form.data['hash']
				else:
					f.hash = file_hash
						
				f.expire = form.cleaned_data['expire']
				f.max_expire = 130
				f.user_name = request.user.username
				f.save()
					
				for afile in request.FILES.getlist('docfile'):
					Attachment(docfile=afile, userfile=f).save()
					
				return redirect('destructible.views.file', file_hash=f.hash)

		else:
			form = UserFileForm()
			uform = UploadForm()
			
		return render(request, 'destructible/file.html', {'form': form, 'uform': uform, 'is_active': is_active})

	else:
	
		if request.method == 'POST':
			fform = NoAuthUserFileForm(request.POST) #unregistered user
			nform = NoAuthUploadForm(request.POST, request.FILES) #smaller file size, one file only
			
			if fform.is_valid() and nform.is_valid():

				f = UserFile() 
				file_hash = human_readable_hash()
		
				f.hash = file_hash
				f.expire = fform.cleaned_data['expire']
				f.max_expire = 65
				f.save()
				docfile = Attachment(docfile = request.FILES['docfile'], userfile=f).save()
				return redirect('destructible.views.file', file_hash=f.hash)

		else:
			nform = NoAuthUploadForm()
			fform = NoAuthUserFileForm()
			
		return render(request, 'destructible/file.html', {'fform': fform, 'nform': nform, 'is_active': is_active, 'contactform': contactform})


def file(request, file_hash):

	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	user_file = UserFile.objects.get(hash=file_hash) #saving this model instance to var

	expire_time = user_file.pub_date + datetime.timedelta(minutes=user_file.expire)
	now = datetime.datetime.now(timezone.utc) #getting current time
	p = user_file.password
	current_user = request.user
	file_user = user_file.user_name
	if p: 
		if request.session.get(user_file.hash):
			return redirect('destructible.views.passwordprotected', file_hash=user_file.hash)
		form = UserFileForm()
		return render(request, 'destructible/password_required.html', {'form': form, 'user_file': user_file, 'is_active': is_active})
	else:
	
		if expire_time >= now:

			user_file = get_object_or_404(UserFile, hash=file_hash)
			current_user = request.user.get_username()
			file_uploader_name = user_file.user_name
			if (current_user) == (file_uploader_name): #tests if user who uploaded is current user
				return render(request, 'destructible/authuploaded.html', {"user_file": user_file, 'is_active': is_active}) #returns template w/ add'l option		
			else:
				return render(request, 'destructible/uploaded.html', {"user_file": user_file, 'is_active': is_active})
		else:
			return redirect('destructible.views.expire_now', uuid=user_file.uuid)

def passwordprotected(request, file_hash):

	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	user_file = UserFile.objects.get(hash__iexact=file_hash) #saving this model instance to var
	expire_time = user_file.pub_date + datetime.timedelta(minutes=user_file.expire)
	now = datetime.datetime.now(timezone.utc) #getting current time

	if expire_time >= now:
		user_file = get_object_or_404(UserFile, hash=file_hash)
		current_user = request.user.get_username()
		file_uploader_name = user_file.user_name
		if (current_user) == (file_uploader_name): #tests if user who uploaded is current user
			return render(request, 'destructible/authuploaded.html', {"user_file": user_file, 'is_active': is_active}) #returns template w/ add'l option		
		else:
			return render(request, 'destructible/uploaded.html', {"user_file": user_file, 'is_active': is_active})
	else:
		return redirect('destructible.views.expire_now', uuid=user_file.uuid)
		
def password_required(request, file_hash):

	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	if request.method == 'POST':
		form = UserFileForm(request.POST)
		
		p = form.data['password']
		user_file = get_object_or_404(UserFile, hash=file_hash)
		up = user_file.password
		if up == p:
			#implement set cookie here
			request.session[user_file.hash] = True
			return redirect('destructible.views.passwordprotected', file_hash=user_file.hash)			#return render('destructible.views.file', file_hash=f.hash)
		else:
			return render(request, 'destructible/password_required.html', {'form': form, 'user_file': user_file, 'is_active': is_active})
	else:
		form = UserFileForm()
		return render(request, 'destructible/password_required.html', {'form': form, 'user_file': user_file, 'is_active': is_active})
		
def expire_now(request, uuid):

	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	user_file = get_object_or_404(UserFile, uuid=uuid)

	time_to_delete = user_file.attachment_set.all()
	
	for entry in time_to_delete:
		entry.docfile.delete()
	
	user_file.delete()
	return redirect('/destructible/expired.html', {'is_active': is_active})

#expire now from console, redirects to console instead of expired template
def expire_now_console(request, uuid):

	user_file = get_object_or_404(UserFile, uuid=uuid)

	time_to_delete = user_file.attachment_set.all()
	
	for entry in time_to_delete:
		entry.docfile.delete()
	
	user_file.delete()
	return redirect('userfilelist')

def extend_time(request, uuid):

	user_file = get_object_or_404(UserFile, uuid=uuid)
	file_hash = user_file.hash
	t = 0

	if (t <= 2) & ((user_file.expire + 15) >= user_file.max_expire):
		t += 1
		user_file.expire = user_file.max_expire
		user_file.save()
		return redirect('destructible.views.file', file_hash=user_file.hash)
	elif (t <= 2):
		t += 1
		user_file.expire += 15
		user_file.save()
		return redirect('destructible.views.file', file_hash=user_file.hash)
	else:
		pass

	return redirect('destructible.views.file', file_hash=user_file.hash)
	
def remove_buttons(request, uuid):
	
	user_file = get_object_or_404(UserFile, uuid=uuid)
	file_hash = user_file.hash
	remove_toggle = user_file.no_buttons
	
	if remove_toggle == True:
		user_file.no_buttons = False
		user_file.save()
		return redirect('destructible.views.file', file_hash=user_file.hash)
	else:
		user_file.no_buttons = True
		user_file.save()
		return redirect('destructible.views.file', file_hash=user_file.hash)
		
def email(request):
	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	if request.method == 'GET':
		contactform = ContactForm()
	else:
		contactform = ContactForm(request.POST)
		c = Contact()
		if contactform.is_valid():
			subject = contactform.cleaned_data['subject']
			from_email = contactform.cleaned_data['from_email']
			message = contactform.cleaned_data['message']
			c.subject = subject
			c.from_email = from_email
			c.message = message
			c.save()
			try:
				send_mail(subject, message, from_email, ['aaron.wieczorek@gmail.com'])
			except BadHeaderError:
				return HttpResponse('Invalid header found.')
			return redirect('thanks')
	return render(request, "destructible/email.html", {'contactform': contactform, 'is_active': is_active})

def thanks(request):

	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	return render(request, "destructible/thanks.html", {'is_active': is_active})
def moreinfo(request):

	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	return render(request, "destructible/moreinfo.html", {'is_active': is_active})
@login_required
@subscription_payment_required
def userfilelist(request):

	if request.user.is_authenticated():
		is_active = subscriber_has_active_subscription(request.user)
	else:
		is_active = False
		
	current_user = request.user.username
	user_file = UserFile.objects.filter(user_name=current_user)

	return render(request, 'destructible/filelist.html', {'user_file': user_file, 'is_active': is_active})
		