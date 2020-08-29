from django.conf.urls import url

from django_sendgrid_tracking import views

app_name = 'django_sendgrid_tracking'
urlpatterns = [
    url(r'event_hooks', views.event_hooks, name='event_hooks'),
]
