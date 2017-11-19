from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import User, Permission
from django.contrib.auth import authenticate, login, logout
from django.db.models import F
from datetime import datetime,timedelta
from hospital import models as hmodels
from models import *
import pdb
import datetime
import random,string

#UTILITY FUNCTIONS
def nop():
    pass

def appid(size=4,nums=string.digits):
    exid=''
    for _ in range(size):
     exid +=random.choice(nums)
    return exid

def uniqueid(x):
    code=x+appid()
    qs=Appointment.objects.filter(excelid=code).exists()
    if qs:
        uniqueid()
    return code

#Homepage
def index(request):
    if request.user.username == '':
        # template = loader.get_template('users/login.html')
        # return HttpResponse(template.render({}, request))
        return HttpResponseRedirect('/login')
    else:
        obj = Profile.objects.get(user=request.user)
        if(Doctor.objects.filter(user=obj.profile_id).exists()):
            return HttpResponseRedirect('/home_doctor')
        return HttpResponseRedirect('/home_patient')

#Login
def login_request(request):
    context, perm_list = {}, {}
    if request.method == 'POST':
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                for x in Permission.objects.filter(user=request.user):
                    perm_list[x.codename] = True
                context = {'permissions': perm_list}
                obj = Profile.objects.get(user=request.user)
                if(Doctor.objects.filter(user=obj.profile_id).exists()):
                    return HttpResponseRedirect('/home_doctor')
                return HttpResponseRedirect('/home_patient')
    context['success']=False
    template = loader.get_template('users/login.html')
    return HttpResponse(template.render(context, request))


#To register
def create_user(request):
    # perm_list={}
    # for x in Permission.objects.filter(user=request.user):
    #     perm_list[x.codename]=True
    #context = {'permissions':perm_list}
    context={}
    if request.method == 'POST':
        name = request.POST.get('name', '')
        username = request.POST.get('username', '')
        emailid = request.POST.get('emailid', '')
        password = request.POST.get('password', '')
        phoneno = request.POST.get('phoneno', '')
        location = request.POST.get('location', '')
        profile_picture = request.POST.get('profile_picture', None)
        user = User.objects.create_user(username, emailid, password)
        user.save()
        kwargs = {'user': user, 'name': name, 'location': location, 'profile_picture':profile_picture,
                  'hospital': hospital, 'phoneno': phoneno}
        profile = Profile(**kwargs)
        profile.save()
        if request.POST.get('type', '') == 'Doctor':
            specialisation = request.POST.get('specialisation', '')
            licence = request.POST.get('licence', '')
            kwargs = {'user': profile, 'specialisation': specialisation, 'licence': licence}
            doctor = Doctor(**kwargs)
            doctor.save()
            user.save()
        context['success'] = True
        template = loader.get_template('users/user_created.html')
        return HttpResponse(template.render(context, request))
    template = loader.get_template('users/register.html')
    return HttpResponse(template.render(context, request))


#Display homepage - list appointments
@login_required(login_url='login.html')
def my_appointments(request):
    perm_list={}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename]=True
    context = {'permissions':perm_list}
    obj=Profile.objects.get(user=request.user)
    context['appointments'] = Appointment.objects.filter(patient=obj.profile_id)
    context['Doctor']=0
    context['name']=obj.name
    template = loader.get_template('users/patienthome.html')
    return HttpResponse(template.render(context, request))


#To filter possible appointment times
@login_required(login_url='login.html')
def find_appointment(request):
    perm_list = {}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename] = True
    context = {'permissions': perm_list}
    obj=Profile.objects.get(user=request.user)
    context['Doctor']=0
    context['name']=obj.name

    if request.method == 'POST':
        search_criteria = {}

        #Find Doctors first
        special = request.POST.get('specialization', '')
        search_criteria['specialization'] = special if (special) else nop()
        doc = Doctor.objects.filter(**search_criteria)

        doctor_name = request.POST.get('doctor', '')
        doctors = []
        if (doctor_name):
            for obj in doc:
                if (obj.user.name == doctor_name):
                    doctors.append(obj)
        else:
            doctors = doc
        date = request.POST.get('date', '')
        q = Session.objects.filter(doctor=doctors[0],date=date).exclude(num_patients=F('limit_option'))

        for i in range(1,len(doctors)):
            q = q | Session.objects.filter(doctor=doctors[i],date=date).exclude(num_patients=F('limit_option'))
        context['result'] = q
        template = loader.get_template('users/viewdoctors.html')
        return HttpResponse(template.render(context, request))

    template = loader.get_template('users/findappointment.html')
    return HttpResponse(template.render(context, request))


#To schedule appointment
@login_required(login_url='login.html')
def schedule_appointment(request,**kwargs):
    perm_list={}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename]=True
    context = {'permissions':perm_list}
    if request.method == 'POST':
        #appointment_id = request.POST.get('appointment_id','') #Indicates if new/edit
        session_id = kwargs['sid']
        session = Session.objects.get(session_id=session_id)
        patient = request.user
        token, approx_time = session.increment()
        kwargs = {'session': session, 'doctor': session.doctor, 'hospital': session.hospital, 'patient':patient,
                  'token':token, 'approx_time':approx_time}
        context['appointment'] = Appointment(**kwargs)
    template = loader.get_template('users/confirmappointment.html')
    return HttpResponse(template.render(context, request))

#To confirm appointment
@login_required(login_url='login.html')
def confirmappointment(request):
    context = {'confirmed':1}
    if request.method == 'POST':
        confirm_flag = request.POST.get('confirm_flag', '')
        appointment_id = request.POST.get('appointment_id', '')
        if confirm_flag=='No':
            Appointment.objects.get(id=appointment_id).remove()
            context['confirmed'] = 0
    return HttpResponseRedirect('/home_patient')
    # template = loader.get_template('.html')
    # return HttpResponse(template.render(context, request))


#To edit appointment - Redirect to new appointment with prefilled values
@login_required(login_url='login.html')
def editappointment(request,**kwargs):
    #Only come here after the user is sure he/she wants to surrender token
    context = {'deleted':0}
    context['old_data']=Appointment.objects.get(appointment_id=kwargs['aid'])
    if request.method=='POST':
        appointment_id = kwargs['aid']
        appointment = Appointment.objects.get(appointment_id=appointment_id)
        #Update other appointments in same session
        time_delta = appointment.session.approx_time
        Appointment.objects.filter(**{'session':appointment.session}).update(approx_time=F('approx_time')-time_delta)
        #Reschedule Google Calendar and send mail
        appointment.session.decrement()
        context['appointment']=appointment
        appointment.delete()
        context['deleted']=1
        return HttpResponseRedirect('/home_patient')
    template = loader.get_template('users/editform.html')
    return HttpResponse(template.render(context, request))

#To delete appointment
@login_required(login_url='login.html')
def deleteappointment(request):
    #Only come here after the user is sure he/she wants to surrender token
    context = {'deleted':0}
    if request.method=='POST':
        appointment_id = request.POST.get('appointment_id', '')
        appointment = Appointment.objects.get(id=appointment_id)
        #Update other appointments in same session
        time_delta = appointment.session.approx_time
        Appointment.objects.filter(**{'session':appointment.session}).update(approx_time=F('approx_time')-time_delta)
        #Reschedule Google Calendar and send mail
        appointment.session.decrement()
        appointment.delete()
        context['deleted'] = 1
    template = loader.get_template('.html')
    return HttpResponse(template.render(context, request))

# ------------------------------------------------------------------------------ #

#Doctor homepage - List Appointments
def doctor_home(request):
    perm_list = {}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename] = True
    context = {'permissions': perm_list}
    obj = Profile.objects.get(user=request.user)
    #context['appointments'] = Appointment.objects.filter(doctor=Doctor.objects.get(user=request.user)).order_by('approx_time')
    context['session'] = Session.objects.filter(doctor=Doctor.objects.get(user=obj.profile_id)).order_by()
    context['name'] = obj.name
    context['Doctor'] = True

    template = loader.get_template('users/doctorhome.html')
    return HttpResponse(template.render(context, request))


#Doctor hospitals - List Hospitals
def my_hospitals(request):
    perm_list = {}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename] = True
    context = {'permissions': perm_list}
    obj = Profile.objects.get(user=request.user)
    context['hospitals'] = DoctorList.objects.filter(doctor=Doctor.objects.get(user=obj.profile_id))
    context['name'] = obj.name
    context['Doctor'] = True
    template = loader.get_template('users/myhospitals.html')
    return HttpResponse(template.render(context, request))

#View session arrangement in a particular hospital
def view_session(request,**kwargs):
    perm_list = {}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename] = True
    context = {'permissions': perm_list}
    hospital_id = kwargs['hid']
    hospital = Hospital.objects.get(hospital_id=hospital_id)
    obj = Profile.objects.get(user=request.user)
    context['name']=obj.name
    context['hname']=hospital.hospital_name
    context['Doctor']=True
    context['session'] = Session.objects.filter(doctor=Doctor.objects.get(user=obj.profile_id),hospital=hospital).order_by('date')
    template = loader.get_template('users/hospsessions.html')
    return HttpResponse(template.render(context, request))


def toggle_status(request):
    perm_list = {}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename] = True
    context = {'permissions': perm_list}
    hospital_id = request.POST.get('hospital_id ', '')
    hospital = hmodels.Hospital.objects.get(hospital_id=hospital_id)
    hmodels.Doctorlist.objects.get(doctor=Doctor.objects.get(user=request.user), hospital=hospital).update(verify=not F('verify'))
    template = loader.get_template('.html')
    return HttpResponse(template.render(context, request))


def change_profile_pic(request):
    profile_picture = request.POST.get('profile_picture', None)
    Profile(user=request.user).update(profile_picture=profile_picture)
    Profile.save()
    context = {'success':True}
    template = loader.get_template('.html')
    return HttpResponse(template.render(context, request))


def page_not_found(request):
    template=loader.get_template('users/404.html')
    return HttpResponse(template.render({}, request))