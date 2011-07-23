from django.contrib import admin
from services.models import FacilityType, Facility, Submission

admin.site.register(FacilityType)
admin.site.register(Facility)
admin.site.register(Submission)