from django_restapi.model_resource import Collection
from django_restapi.resource import Resource
from django_restapi.responder import JSONResponder
from django_restapi.authentication import HttpBasicAuthentication
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from models import Facility, Submission, FacilityType, User
from web_services import GoogleMapService
import logging
import json

def get_location(param):
	try:
		return Point(float(param['long']),float(param['lat']))
	except KeyError:
		logging.debug('Coordinates are not provided. Using Google Map API to infer them from address.')
		try:
			with GoogleMapService() as service:
				return Point(*service.get_coordinates(param['address']))
		except KeyError:
			logging.error('Both coordinates and address are missing')
			return None

class FacilityCollection(Collection):
	def read(self,request):
		distance_threshold = request.GET.get('km',300)
		distance_filter = (get_location(request.GET),D(km=distance_threshold))
		filtered_set = Facility.objects.filter(location__dwithin=distance_filter).order_by('distance')
		return self.responder.list(request,filtered_set)
	
class SubmissionCollection(Collection):
	def create(self,request):
		submission = self._save_submission(request)
		facility = self._create_or_update_facility(submission)
		return self.responder.list(request,facility)
		
	def update(self,request):
		return self.create(request)
		
	def _save_submission(self,request):
		def get_type(request):
			try:
				return FacilityType.objects.get(name=request.POST['type'])
			except KeyError:
				return None
		
		submit_args = {
				'submitter':request.user,
				'raw':repr(request.POST),
				'name':request.POST.get('name',None),
				'address':request.POST.get('address',None),
				'phone':request.POST.get('phone',None),
				'type':get_type(request),
				'location':get_location(request.POST)
			}
		return Submission(**submit_args).save()
		
	def _create_or_update_facility(self,submission,distance_threshold=1):
		"""
		Gets nearby submissions to determine duplicate by comparing name and submitter
		If the submitted facility already exists, it is updated; if not, it is created
		"""
		# get facility/submissions within the set distance (in km)
		distance_filter = (submission.location,D(km=distance_threshold))
		try:
			for facility in Facility.objects.filter(location__dwithin=distance_filter).order_by('distance'):
				if not facility.name or facility.name == submission.name: # TODO: use proper string comparison function
					for field in 'name address phone type'.split():
						new_value = getattr(submission,field,None)
						existing_value = getattr(facility,field,None)
						if new_value and not existing_value:
							# currently keeps existing value
							# TODO: if a value already exists, select the value with the highest submitter rating
							setattr(facility,field,getattr(submission,field,None))
					facility.location = Submission.objects.filter(location__dwithin=distance_filter).centroid()
					return facility.save()
		except AttributeError:
			logging.info('The submission is new')
			facility_args = {}
			for field in 'name address type location'.split():
				facility_args[field] = getattr(submission,field)
			return Facility(**facility_args).save()

facility_resource = FacilityCollection(
		queryset = Facility.objects.all(),
		permitted_methods = ['GET'],
		responder = JSONResponder(paginate_by = 10),
	)
	
submission_resource = SubmissionCollection(
		queryset = Submission.objects.all(),
		permitted_methods = ('GET','POST','PUT'),
		responder = JSONResponder(paginate_by = 10),
		# authentication = HttpBasicAuthentication(),
	)
