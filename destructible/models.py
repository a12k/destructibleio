import uuid

from django.db import models
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from django.db.models.signals import post_save

from django.dispatch import receiver
from djstripe.utils import subscriber_has_active_subscription
		
class UserFile(models.Model):

	hash = models.CharField(max_length=32, unique=True, blank=True)
	pub_date = models.DateTimeField(auto_now_add=True)
	expire = models.PositiveIntegerField(default=15, validators=[MaxValueValidator(7215, "The value should be less than %(limit_value)s.")])
	max_expire = models.IntegerField(75)
	password = models.CharField(max_length=32)
	user_name = models.CharField(max_length=100, default='nouser') 
	edit_expire_now = models.BooleanField(default=False)
	uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
	no_buttons = models.BooleanField(default=False)
	
	def __str__(self):
		return '%s, %s, %s, %s' % (self.hash, self.user_name, self.pub_date, self.expire)

class Attachment(models.Model):	
	
	def generate_filename(self, filename):
		url = "%s/%s" % (self.userfile.uuid, filename)
		return url
	
	userfile = models.ForeignKey(UserFile, verbose_name=('UserFile'), null=True, blank=True, on_delete=models.CASCADE)
	docfile = models.FileField(upload_to=generate_filename)
	
	def __str__(self):
		return '%s %s %s' % (self.docfile, self.userfile, self.id)

#extends standard User model to add a field to test if user has paid/is current
class UserProfile(models.Model):

	user = models.OneToOneField(User, related_name='active')
	is_subscribed = models.BooleanField(default=False)

	def __str__(self):
		return self.username

	def __unicode__(self):
		return self.username

	@cached_property
	def has_active_subscription(self):
		return subscriber_has_active_subscription(self)

#receiver to auto-create UserProfile model everytime new User created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)
	
class Contact(models.Model):
	from_email = models.EmailField(blank=False)
	subject = models.CharField(max_length=150, blank=True)
	message = models.CharField(max_length=1000)
	
	def __str__(self):
		return '%s, %s' % (self.from_email, self.subject)