# Create your views here.

from django.shortcuts import render_to_response
from healthcare_mapping.services.models import FacilityType
from healthcare_mapping.services.rest_views import facility_resource, submission_resource, get_location
from healthcare_mapping.services.web_services import GoogleMapService
from models import User

def map(request):
	values = {
			'types':FacilityType.objects.all(),
			'center':(55.897, -3.144),
		}
	center = get_location(request.GET)
	if center: values['center'] = center.y, center.x
	return render_to_response('map.html',values)

def login(request):
	pass
