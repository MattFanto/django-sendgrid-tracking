from django.contrib import admin

# Register your models here.
from django_sendgrid_tracking.models import MailCategory, SentMail, SendGridNotification

admin.site.register(MailCategory)
admin.site.register(SentMail)
admin.site.register(SendGridNotification)
