# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from . import forms
from django.http import HttpResponseNotAllowed,HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404
#from django.contrib.sessions.backends.base.SessionBase
from datetime import datetime, timedelta
from django.template import loader
from users.models import *


def createsession(hospital,ndate, date, nstart_time, nnum_patients, ndoctor, napprox_time, nend_time, nlimit_option):
    sess = Session(hospital=hospital,day_of_week = ndate, date = date, start_time = nstart_time, num_patients = nnum_patients, num_reg_patients = 0,doctor = ndoctor, approx_time = napprox_time, end_time = nend_time, limit_option = nlimit_option)
    sess.save()
    #Need to add hospital to the table

def registerdoctor(hospital, doctor):
    sess = DoctorList(hospital = hospital, doctor = doctor)
    sess.save()

def getlistofappointment(sess):
    return umodel.Appointment.objects.filter(session = sess)

def getlistofdoctors(hospital):
    return models.DoctorList.objects.filter(hospital = hospital)

def getday(date):
    date.weekday()


def hospital_home(request,**kwargs):
    hospitalid = kwargs['hid']
    if request.method == 'POST':
        hospital = request.POST.get('')
        request.session['hospital_id'] = hospital
    template = loader.get_template('users/hospitalhome.html')
    query = Hospital.objects.get(hospital_id = hospitalid)
    propic = query.hospital_image
    hospitalname = query.hospital_name
    user = request.user
    profile = Profile.objects.get(user = user)
    return HttpResponse(template.render({'profile':profile, 'hospital':hospitalname, 'hospital_image':propic ,'hid':hospitalid}, request))
        
# Function for hospital to create a session
def createsessionview(request,**kwargs):
    hospital_id = kwargs['hid']
    url='/hospital/'+kwargs['hid']+'/home'
    if request.method == 'POST':
        day = request.POST.get('hospital_id')
        start_time = request.POST.get('stime')
        num_patients = request.POST.get('num')
        doctor1 = request.POST.get('doctor')
        doctor = Doctor.objects.get(user = doctor1)
        approx_time = request.POST.get('apptime')
        end_time = request.POST.get('etime')
        hospital = Hospital.objects.get(hospital_id=hospital_id)
        limit_option = request.POST.get('loption')
        j = datetime.datetime.now()
        for i in range(0,7):
            j += timedelta(days = i)
            createsession(hospital,day, j, start_time, num_patients, doctor, approx_time, end_time, limit_option)
        return HttpResponseRedirect(url)

    template = loader.get_template('users/createsession.html')
    user = request.user
    profile = Profile.objects.get(user = request.user)
    return HttpResponse(template.render({'profile':profile, 'success':True , 'hid':hospital_id}, request)) #Redirect to home page

# Function for hospital to register a new doctor into their system
def regdoctor(request):
    if request.method == 'POST':
        doctor = request.POST.get('doctor')
        hospital1 = request.POST.get('hospital_id')
        hospital = Hospital.objects.get(hospital_id=hospital1)
        registerdoctor(hospital, doctor)
    template = loader.get_template('users/regdoctor.html')
    user = request.user
    profile = Profile.objects.get(user = request.user)
    return HttpResponse(template.render({'profile':profile, 'success': True}, request)) #redirect to home page

def reghospital(request,**kwargs):
    url='/hospital/'+kwargs['hid']+'/home'
    if request.method == 'POST':
        hospital_name = request.POST.get('hospital')
        location = request.POST.get('location')
        hospital_description = request.POST.get('description')
        hospital_image = request.POST.get('image')
        mod = Hospital(hospital_name=hospital_name,location=location, hospital_description=hospital_description, hospital_image=hospital_image,admin=Profile.objects.get(user=request.user))
        mod.save()
        return HttpResponseRedirect(url)
    
    template = loader.get_template('users/hospitals.html')
    user = request.user
    profile = Profile.objects.get(user = user)
    return HttpResponse(template.render({'profile':profile, 'success':True ,'hid':kwargs['hid']}, request))

# Given a date get all the sessions.
def gettimetablebydate(request,**kwargs):
    hospital = kwargs['hid']
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
