from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User, Permission
from django.contrib.auth import authenticate, login, logout
from django.db.models import F
from datetime import datetime,timedelta
from hospital import models as hmodels
from models import *

#UTILITY FUNCTIONS
def nop():
    pass


#Homepage
def index(request):
    if request.user == None:
        template = loader.get_template('templates/login.html')
        return HttpResponse(template.render({}, request))
    else:
        template = loader.get_template('templates/index.html')
        return HttpResponse(template.render({}, request))


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
                template = loader.get_template('.html')
                return HttpResponse(template.render(context, request))
    context['success']=False
    template = loader.get_template('templates/login.html')
    return HttpResponse(template.render(context, request))


#To register
def create_user(request):
    perm_list={}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename]=True
    context = {'permissions':perm_list}
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
    template = loader.get_template('templates/user_created.html')
    return HttpResponse(template.render(context, request))


#Display homepage - list appointments
@login_required(login_url='login.html')
def my_appointments(request):
    perm_list={}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename]=True
    context = {'permissions':perm_list}
    context['appointments'] = Appointment.objects.filter(patient=request.user)
    template = loader.get_template('.html')
    return HttpResponse(template.render(context, request))


#To filter possible appointment times
@login_required(login_url='login.html')
def find_appointment(request):
    perm_list = {}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename] = True
    context = {'permissions': perm_list}
    if request.method == 'POST':
        search_criteria = {}
        #Find Doctors first
        specialisation = request.POST.get('specialisation', '')
        search_criteria['specialisation'] = specialisation if (specialisation) else nop()
        doctor_name = request.POST.get('doctor', '')
        search_criteria['user.name'] = doctor_name if (doctor_name) else nop()
        doctors = Doctor.objects.get(**search_criteria)
        date = request.POST.get('date', '')
        date = date.strptime(date, "%d/%m/%Y")
        q = hmodels.Session.objects.filter(doctor=doctors[0],date=date).exclude(number_of_patients__eq=F('limit_option'))
        for i in range(1,len(doctors)):
            q = q | hmodels.Session.objects.filter(doctor=doctors[i],date=date).exclude(number_of_patients__eq=F('limit_option'))
        context['result'] = q
    template = loader.get_template('.html')
    return HttpResponse(template.render(context, request))


#To schedule appointment
@login_required(login_url='login.html')
def schedule_appointment(request):
    perm_list={}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename]=True
    context = {'permissions':perm_list}
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id','') #Indicates if new/edit
        session_id = request.POST.get('session_id', '')
        session = hmodels.Session.objects.get(id=session_id)
        patient = request.user
        token, approx_time = session.increment()
        kwargs = {'session': session, 'doctor': session.doctor, 'hospital': session.hospital, 'patient':patient,
                  'token':token, 'approx_time':approx_time}
        context['appointment'] = Appointment(**kwargs)
    template = loader.get_template('.html')
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
    template = loader.get_template('.html')
    return HttpResponse(template.render(context, request))


#To edit appointment - Redirect to new appointment with prefilled values
@login_required(login_url='login.html')
def editappointment(request):
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
        context['appointment']=appointment
        appointment.delete()
        context['deleted']=1
    template = loader.get_template('.html')
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
    #context['appointments'] = Appointment.objects.filter(doctor=Doctor.objects.get(user=request.user)).order_by('approx_time')
    context['session'] = hmodels.Sessions.objects(doctor=Doctor.objects.get(user=request.user)).order_by()
    template = loader.get_template('.html')
    return HttpResponse(template.render(context, request))


#Doctor hospitals - List Hospitals
def my_hospitals(request):
    perm_list = {}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename] = True
    context = {'permissions': perm_list}
    context['hospitals'] = hmodels.DoctorList.objects.filter(doctor=Doctor.objects.get(user=request.user)).order_by(
        'approx_time')
    template = loader.get_template('.html')
    return HttpResponse(template.render(context, request))

#View session arrangement in a particular hospital
def view_session(request):
    perm_list = {}
    for x in Permission.objects.filter(user=request.user):
        perm_list[x.codename] = True
    context = {'permissions': perm_list}
    hospital_id = request.POST.get('hospital_id ', '')
    hospital = hmodels.Hospital.objects.get(hospital_id=hospital_id)
    context['session'] = hmodels.Session.objects.filter(doctor=Doctor.objects.get(user=request.user),hospital=hospital).order_by('date').distinct('day_of_week')
    template = loader.get_template('.html')
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