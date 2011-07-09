from django_restapi.model_resource import Collection
from django_restapi.resource import Resource
from django_restapi.responder import JSONResponder
from django_restapi.authentication import HttpBasicAuthentication
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from models import Facility, Submission, FacilityType
from web_services import GoogleMapServices
import logging
import json

class FacilityCollection(Collection):
	FILTERS = { # add new search functions here
			'distance':(self._search_by_distance,('lat','long')),
			'profile':(self._search_by_profile,('conditions')),
		}	
	
	def read(self,request):
		filter = request.GET.get('filter',None)
		try:
			function, args = FILTERS[filter]
			return function(*request.GET.get(arg,None) for arg in args)
		except KeyError:
			logging.warning('User tried to search by invalid filter '+filter)
		
	def _search_by_distance(self,lat,long):
		"""
		Takes a JSON tuple of coordinates and distance in *kilometers*
		"""
		return Facility.objects.distance(Point(float(lat),float(long))).order_by('distance')
		
	def _search_by_profile(self,conditions):
		"""
		Takes a JSON object that maps the fields to their respective restriction
		"""
		return Facility.objects.get(**json.loads(conditions))
	
class SubmissionCollection(Collection):
	def create(self,request):
		submission = self._save_submission(request)
		return self._create_or_update_facility(submission)
		
	def _save_submission(self,request):
		def get_type(request):
			try:
				return FacilityType.objects.get(name=request.POST['type'])
			except KeyError:
				return None
		
		def get_location(request):
			try:
				return Point(float(request.POST['long']),float(request.POST['lat']))
			except KeyError:
				logging.debug('Coordinates are not provided. Using Google Map API to infer them from address.')
				try:
					with GoogleMapServices() as service:
						return Point(*services.get_coordinates(request.POST['address']))
				except KeyError:
					logging.error('Both coordinates and address are missing')
		
		submit_args = {
				'submitter':request.user,
				'raw':repr(request.POST),
				'name':request.POST.get('name',None),
				'address':request.POST.get('address',None),
			}
		type = get_type(request)
		if type: submit_args['type'] = type
		location = get_location(request)
		if location: submit_args['location'] = location
		return Submission(**submit_args).save()
		
	def _create_or_update_facility(self,submission,distance_threshold=1):
		"""
		Gets nearby submissions to determine duplicate by comparing name and submitter
		If the submitted facility already exists, it is updated; if not, it is created
		"""
		# get facility/submissions within the set distance (in km)
		distance_filter = (submission.location,D(km=distance_threshold))
		try:
			facility = Facility.objects.filter(location__dwithin=distance_filter).order_by('distance').next()
			facility.location = Submission.objects.filter(location__dwithin=distance_filter).centroid()
			for field in 'name address type'.split():
				new_value = getattr(submission,field,None)
				existing_value = getattr(facility,field,None)
				if new_value and not existing_value:
					# TODO: if a value already exists, select the value with the highest submitter rating
					setattr(facility,field,getattr(submission,field,None))
			facility.save()
		except AttributeError:
			logging.info('The submission is new')
			facility_args = {}
			for field in 'name address type location'.split():
				facility_args[field] = getattr(submission,field)
			return Facility(**facility_args).save()

facility_resource = FacilityCollection(
		permitted_methods = ('GET'),
		responder = JSONResponder(paginate_by = 10),
	)
	
submission_resource = SubmissionCollection(
		permitted_methods = ('GET','POST','PUT'),
		responder = JSONResponder(paginate_by = 10),
		authentication = HttpBasicAuthentication(),
	)
