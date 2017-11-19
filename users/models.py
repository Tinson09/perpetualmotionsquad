# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
import datetime
from datetime import timedelta


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
    profile_id = models.CharField(primary_key=True, max_length=6)
    dob = models.DateTimeField()
    name = models.CharField(max_length=30)
    profile_picture = models.ImageField()
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=50)

    def __str__(self):
        return self.profile_id


class OTP(models.Model):
    user = models.ForeignKey(Profile)
    OTP = models.CharField(max_length=6)


class Hospital(models.Model):
    hospital_id = models.IntegerField(primary_key=True)
    hospital_name = models.CharField(max_length = 50)
    admin = models.ForeignKey(Profile, null=False)
    location = models.TextField()
    hospital_description = models.TextField()
    hospital_image = models.ImageField()

    def __str__(self):
        return self.hospital_name
        
    class Meta:
        db_table = "Hospital"


class Doctor(models.Model):
    user = models.ForeignKey(Profile)
    hospital = models.ForeignKey(Hospital)
    specialization = models.CharField(max_length=50)
    licence = models.CharField(max_length=50)
    verified = models.BooleanField(default=False)


class Session(models.Model):
    days = (('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'))
    date = models.DateField()
    day_of_week = models.CharField(max_length = 9, choices = days)
    start_time = models.TimeField()
    session_id=models.IntegerField()
    hospital = models.ForeignKey(Hospital)
    num_patients = models.IntegerField()
    num_reg_patients = models.IntegerField()
    doctor = models.ForeignKey(Doctor)
    approx_time = models.DurationField(default=timedelta(minutes=20))
    end_time = models.TimeField()
    choice = (('n', 'Number of Patients'), ('t', 'Approximate Time'), ('b', 'Both'))
    limit_option = models.CharField(max_length = 1, choices = choice) 
    def increment(self):
        self.num_reg_patients += 1
        return (self.num_reg_patients, self.num_reg_patients*self.approx_time)
    def decrement(self):
        self.num_reg_patients -= 1

    class Meta:
        db_table = "Session"
        
 
class Appointment(models.Model):
    appointment_id=models.IntegerField()
    session = models.ForeignKey(Session)
    doctor = models.ForeignKey(Doctor)
    hospital = models.ForeignKey(Hospital)
    patient = models.ForeignKey(Profile)
    token = models.IntegerField()
    approx_time = models.DateTimeField()


class DoctorList(models.Model):
    hospital = models.ForeignKey(Hospital)
    doctor = models.ForeignKey(Doctor)
    verify = models.BooleanField()
    class Meta:
        db_table = "DoctorList"