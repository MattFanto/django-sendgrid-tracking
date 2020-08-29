from django.conf.urls import url, include
from django.urls import path

from . import views

urlpatterns = [
    path(r'', include('django_sendgrid_tracking.urls')),
    path('tests/send-email', views.send_mail)
]
