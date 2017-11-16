# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from users.models import *

class Hospital(models.Model):
    hospital_id = models.IntegerField(primary_key=True)
    hospital_name = models.CharField(max_length = 50)
    admin = models.ForeignKey(Profile, null=False)
    location = models.TextField()
    hospital_description = models.TextField()
    hospital_image = models.ImageField()

    class Meta:
        db_table = "Hospital"

class Session(models.Model):
    days = (('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'))
    date = models.DateField()
    day_of_week = models.CharField(max_length = 9, choices = days)
    start_time = models.TimeField()
    hospital = models.ForeignKey(Hospital)
    num_patients = models.IntegerField()
    num_reg_patients = models.IntegerField()
    doctor = models.ForgeinKey(Doctor)
    approx_time = models.DurationField()
    end_time = models.TimeField()
    choice = (('n', 'Number of Patients'), ('t', 'Approximate Time'), ('b', 'Both'))
    limit_option = models.CharField(max_length = 1, choices = choice) 
    def increment(self):
        num_reg_patients += 1
        return (num_reg_patients, num_reg_patients*approx_time)
    def decrement(self):
        num_reg_patients -= 1

    class Meta:
        db_table = "Session"

class DoctorList(models.Model):
    hospital = models.ForgeinKey(hospital)
    doctor = models.ForgeinKey(Doctor)
    verify = models.BooleanField()
    class Meta:
        db_table = "DoctorList"