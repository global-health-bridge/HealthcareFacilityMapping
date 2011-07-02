from django.conf.urls.defaults import *

urlpatterns = patterns('rest_views',
		(r'^restful/facilities/(.*)?/?$', 'facility_resource'),
		(r'^restful/user/(.*)?/?$', 'user_resource'),
		(r'^restful/submissions/(.*)?/?$', 'submission_resource'),
	)
