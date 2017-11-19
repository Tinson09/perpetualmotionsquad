from django.conf.urls import url
from users import views
from hospital import views as hospview

urlpatterns = [
                # Matches any html file - to be used for gentella
                # Avoid using your .html in your resources. Or create a separate django app.
                url(r'login$', views.login_request, name='login'),
                url(r'index/$', views.index, name='index'),
                url(r'home_patient$', views.my_appointments, name='home_patient'),
                url(r'home_patient/find$', views.find_appointment, name='home_patient'),
                url(r'home_patient/delete/(?P<aid>[\w,()-]+)$', views.editappointment, name='home_patient'),
                 url(r'home_patient/schedule/(?P<sid>[\w,()-]+)$', views.schedule_appointment, name='schedule_appointment'),
                url(r'home_doctor$', views.doctor_home, name='home_doctor'),
                url(r'home_doctor/hospitals/(?P<hid>[\w,()-]+)$',views.view_session,name='view_session'),
                url(r'home_doctor/hospitals$', views.my_hospitals, name='home_doctor'),
                url(r'hospital/(?P<hid>[\w,()-]+)/home$', hospview.hospital_home, name='hospital_home'),
                 url(r'hospital/(?P<hid>[\w,()-]+)/addhospital$', hospview.reghospital, name='reg_hospital'),
                url(r'hospital/(?P<hid>[\w,()-]+)/adddoctor$', hospview.regdoctor, name='reg_doctor'),
                url(r'hospital/(?P<hid>[\w,()-]+)/createsession$', hospview.createsessionview, name='create_session'),
                url(r'register$', views.create_user, name='register'),
                url(r'.*$', views.page_not_found, name='pagenotfound'),
              ]
