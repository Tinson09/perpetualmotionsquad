# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from users.models import Profile,Doctor,Hospital,DoctorList,Appointment,Session
# Register your models here.

admin.site.register(Profile)
admin.site.register(Doctor)
admin.site.register(Hospital)
admin.site.register(DoctorList)
admin.site.register(Appointment)
admin.site.register(Session)