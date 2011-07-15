# Create your views here.

from django.shortcuts import render_to_response
from healthcare_mapping.services.rest_views import FacilityCollection, SubmissionCollection
from healthcare_mapping.services.web_services import GoogleMapService
from models import User

def map(request):
	return render_to_response('map.html',{})

def login(request):
	pass
