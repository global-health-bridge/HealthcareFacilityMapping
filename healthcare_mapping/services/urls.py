from django.conf.urls.defaults import *

urlpatterns = patterns('healthcare_mapping.services.rest_views',
		(r'^restful/facility/(.*)', 'facility_resource'),
		(r'^restful/submission/(.*)', 'submission_resource'),
	)
