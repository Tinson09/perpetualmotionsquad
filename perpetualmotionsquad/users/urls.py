from django.conf.urls import url
from users import views

urlpatterns = [
                # Matches any html file - to be used for gentella
                # Avoid using your .html in your resources. Or create a separate django app.
                url(r'^.*login.html', views.login, name='login'),
                url(r'.*.html', views.index, name='index'),
              ]
