from django_restapi.model_resource import Collection
from django_restapi.resource import Resource
from django_restapi.responder import JSONResponder
from django_restapi.authentication import HttpBasicAuthentication
from django.contrib.gis.geos import Point
from models import Facility, Submission, FacilityType

class FacilityCollection(Collection):
	def read(self,request):
		pass
	
	def search_by_distance(self,location,distance):
		pass
		
	def search_by_profile(self,field,condition):
		pass
	
class SubmissionCollection(Collection):
	def create(self,request):
		submission = self.save_submission(request)
		return self.create_or_update_facility(submission)
		
	def save_submission(self,request):
		def get_type(request):
			try:
				return FacilityType.objects.get(name=request.POST['type'])
			except KeyError:
				return None
		
		def get_location(request):
			try:
				return Point(request.POST['lat'],request.POST['long'])
			except KeyError:
				pass # TODO: log missing location, run mapapi with address

		submit_args = {
				'submitter':request.user,
				'raw':repr(request.POST),
				'name':request.POST.get('name',''),
				'address':request.POST.get('address',''),
			}
		type = get_type(request)
		if type: submit_args['type'] = type
		location = get_location(request)
		if location: submit_args['location'] = location
		
		submission = Submission(**submit_args)
		submission = Submission.save()
		return submission
		
	def create_or_update_facility(self,submission):
		pass
		# TODO: get nearby submissions to determine duplicates by comparing name and submitter

facility_resource = FacilityCollection(
		queryset = Facility.objects.all(),
		permitted_methods = ('GET'),
		responder = JSONResponder(paginate_by = 10),
	)
	
submission_resource = SubmissionCollection(
		queryset = Submission.objects.all(),
		permitted_methods = ('GET','PUT'),
		responder = JSONResponder(paginate_by = 10),
		authentication = HttpBasicAuthentication(),
	)
