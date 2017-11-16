# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from hospital.models import Profile

'''
def unique_rand():
    while True:
        code = User.objects.make_random_password(length=4).upper()
        if not Profile.objects.filter(user_id=code).exists():
            return code
'''

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # User object contains username, emailID
    user_id = models.CharField(primary_key=True)
    dob = models.DateTimeField()
    name = models.CharField(max_length=30)
    profile_picture = models.ImageField()
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=50)


class OTP(models.Model):
    user = models.ForeignKey(Profile)
    OTP = models.CharField(max_length=6)


class Doctor(models.Model):
    user = models.ForeignKey(Profile)
    hospital = hmodels.ForeignKey(Hospital)
    specialization = models.CharField(max_length=50)
    licence = models.CharField(max_length=50)
    verified = models.BooleanField(initial=False)

class Appointment(models.Model):
    session = hmodels.ForeignKey(Session)
    doctor = models.ForeignKey(Doctor)
    hospital = hmodels.ForeignKey(Hospital)
    patient = models.ForeignKey(Profile)
    token = models.IntegerField()
    approx_time = models.DateTimeField()


