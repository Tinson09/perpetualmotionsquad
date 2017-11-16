# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import forms
from . import models
from users import models as umodel
from django.shortcuts import render
from django.views import View
from django.core.urlresolvers import reverse_lazy
from . import forms
from django.http import HttpResponseNotAllowed
from django.shortcuts import render,reverse, HttpResponseRedirect, get_object_or_404,HttpResponse
from django.contrib.sessions.backends.base.SessionBase
from datetime import datetime, timedelta
from django.template import loader


def createsession(ndate, date, nstart_time, nnum_patients, ndoctor, napprox_time, nend_time, nlimit_option, nverify):
    sess = models.Session(day_of_week = ndate, date = date, start_time = nstart_time, num_patients = nnum_patients, num_reg_patients = 0,doctor = ndoctor, approx_time = napprox_time, end_time = nend_time, limit_option = nlimit_option, verify = nverify)
    sess.save()
    #Need to add hospital to the table

def registerdoctor(hospital, doctor):
    sess = models.DoctorList(hospital = hospital, doctor = doctor)
    sess.save()

def getlistofappointment(sess):
    return umodel.Appointment.objects.filter(session = sess)

def getlistofdoctors(hospital):
    return models.DoctorList.objects.filter(hospital = hospital)

def getday(date):
    date.weekday()


def hospital_home(request):
    if request.method == 'POST':
        hospital = request.POST.get('')
        request.session['hospital_id'] = hospital
    template = loader.get_template('.html')
    query = models.Hospital.objects.get(hospital = hospital)
    propic = query.hospital_image
    hospitalname = query.hospital_name
    user = request.user
    profile = umodel.Profile.objects.get(user = user)
    return HttpResponseRedirect({'profile':profile, 'hospital':hospital_name, 'hospital_image':propic})
        
# Function for hospital to create a session
def createsessionview(request):
    if request.method == 'POST':
        day = request.POST.get('')
        start_time = request.POST.get('')
        num_patients = request.POST.get('')
        doctor = request.POST.get('')
        approx_time = request.POST.get('')
        end_time = request.POST.get('')
        limit_option = request.POST.get('')
        j = datetime.now()
        for i in range(0:8:7):
            j += timedelta(days = i)
            createsession(day, j, start_time, num_patients, doctor, approx_time, end_time, limit_option, False)
    template = loader.get_template('.html')
    user = request.user
    profile = umodel.Profile.objects.get(user = user)
    return HttpResponseRedirect(template.render({'profile':profile, 'success':True}, request)) #Redirect to home page

# Function for hospital to register a new doctor into their system
def regdoctor(request):
    if request.method == 'POST':
        doctor = request.POST.get('')
        hospital = request.session['hospital_id']
        registerdoctor(hospital, doctor)
    template = loader.get_template('.html')
    user = request.user
    profile = umodel.Profile.objects.get(user = user)
    return HttpResponseRedirect(template.render({'profile':profile, 'success': True}, request)) #redirect to home page

def reghospital(request):
    if request.method == 'POST':
        hospital_name = request.POST.get('')
        location = request.POST.get('')
        hospital_description = request.POST.get('')
        hospital_image = request.POST.get('')
        mod = models.Hospital(hospital_name=hospital_name,location=loaction, hospital_description=hospital_description, hospital_image=hospital_image)
        mod.save()
    
    template = loader.get_template('.html')
    user = request.user
    profile = umodel.Profile.objects.get(user = user)
    return HttpResponseRedirect(template.render({'profile':profile, 'success':True}, request))

# Given a date get all the sessions.
def gettimetablebydate(request):
    hospital = request.session['hospital_id']
    if request.method == 'POST':
        date = request.POST.get('')
        day = getday(date)
        result = models.Session.objects.filter(hospitalid = hospital)
        result = result.filter(day_of_week = day)
    user = request.user
    profile = umodel.Profile.objects.get(user = user)
    template = loader.get_template('.html')
    return HttpResponseRedirect(template.render({'profile':profile, 'result':result}, request))

def getlistofdoctors(request):
    if request.method == 'POST':
        hospital = request.session['hospital_id']
        result = models.DoctorList.objects.filter(hospital = hospital)
    template = loader.get_template('.html')
    user = request.user
    profile = umodel.Profile.objects.get(user = user)
    return HttpResponseRedirect(template.render({'profile':profile, 'result':result}, request))

def getappointmentsbydoctor(request):
    hospital = request.session['hospital_id']
    if request.method == 'POST':
        doctor = request.POST.get('')
        date = request.POST.get('')
        sess = models.Session.objects.filter(hospital = hospital, doctor = doctor, date = date)
        appointments = umodel.Appointment.objects.filter(session = sess[0])
        for i in sess[1:]:
            appointments += umodel.Appointment.objects.filter(session = i)
    template = loader.get_template('.html')
    user = request.user
    profile = umodel.Profile.objects.get(user = user)
    return HttpResponseRedirect(template.render({'profile':profile, 'appointments':appointments}, request))
