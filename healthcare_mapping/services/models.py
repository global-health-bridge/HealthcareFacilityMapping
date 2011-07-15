from django.contrib.auth.models import User
from django.contrib.gis.db import models
import datetime

# Create your models here.

class FacilityType(models.Model):
	name = models.CharField(max_length=128)
	
	def __unicode__(self):
		return self.name
	
class Facility(models.Model):
	name = models.CharField(max_length=128,null=True)
	type = models.ForeignKey(FacilityType)
	validated = models.BooleanField(default=False)
	address = models.TextField(null=True)
	location = models.PointField(srid=4326,geography=True)
	objects = models.GeoManager()
	
	def __unicode__(self):
		return ' '.join((self.type, self.location.x, self.location.y))

class Submission(models.Model):
	submitter = models.ForeignKey(User)
	datetime = models.DateTimeField('Submission datetime',default=datetime.datetime.now())
	raw = models.TextField('Raw request')
	name = models.CharField(max_length=128,null=True)
	type = models.ForeignKey(FacilityType,null=True)
	address = models.TextField(null=True)
	location = models.PointField(srid=4326,geography=True,null=True)
	objects = models.GeoManager()
	
	def __unicode__(self):
		return ' '.join((self.user.name,self.datetime,self.facility_name))
