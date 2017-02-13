from django.forms import ModelForm
from django import forms
from .models import UserFile, Attachment, Contact
from django.contrib.auth.models import User
from django.db import models
from .fields import MultiFileField
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError

class ActiveUserFileForm(ModelForm):

	password = forms.CharField(widget=forms.PasswordInput, required=False)
	expire = forms.IntegerField(initial=15, validators=[MaxValueValidator(1440)])
	hash = forms.CharField(max_length=32, required=False)
	
	class Meta: 
		model = UserFile
		fields = ['expire']

class UserFileForm(ModelForm):

	password = forms.CharField(widget=forms.PasswordInput, required=False)
	expire = forms.IntegerField(initial=15, validators=[MaxValueValidator(120)])
	hash = forms.CharField(max_length=32, required=False)
	
	class Meta: 
		model = UserFile
		fields = ['expire']
		
class NoAuthUserFileForm(ModelForm):

	password = forms.CharField(widget=forms.PasswordInput, required=False)
	expire = forms.IntegerField(initial=15, validators=[MaxValueValidator(45)], widget=forms.NumberInput(attrs={'class': 'narrow-select'}))
	hash = forms.CharField(max_length=32, required=False)
	
	class Meta: 
		model = UserFile
		fields = ['expire']
		


class UploadForm(ModelForm):

	class Meta:
		model = Attachment
		fields = ['docfile']
		
	docfile = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*20)

	def save(self, commit=True):
		instance = super(UserFileForm, self).save(commit)
		for each in self.cleaned_data['docfile']:
			Attachment.objects.create(docfile=each, userfile=instance)

		return instance		
		
class ActiveUploadForm(ModelForm):

	class Meta:
		model = Attachment
		fields = ['docfile']
		
	docfile = MultiFileField(min_num=1, max_num=5, max_file_size=1024*1024*120)

	def save(self, commit=True):
		instance = super(UserFileForm, self).save(commit)
		for each in self.cleaned_data['docfile']:
			Attachment.objects.create(docfile=each, userfile=instance)

		return instance		

class NoAuthUploadForm(ModelForm):
	
	def validate_file(fieldfile_obj):
		filesize = fieldfile_obj.size
		megabyte_limit = 10.0
		if filesize > megabyte_limit*1024*1024:
			raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
			
	class Meta:
		model = Attachment
		fields = ['docfile']
		
	docfile = forms.FileField(label='Select a file', validators=[validate_file])

	def save(self, commit=True):
		instance = super(UserFileForm, self).save(commit)
		for each in self.cleaned_data['docfile']:
			Attachment.objects.create(docfile=each, userfile=instance)

		return instance
		
class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ('username', 'email', 'password')
		
class ContactForm(ModelForm):
	message = forms.CharField(widget=forms.Textarea)
	class Meta:
		model = Contact
		fields = ['from_email', 'subject', 'message']