from django.apps import AppConfig


class DjangoSendgridEmailConfig(AppConfig):
    name = 'django_sendgrid_tracking'

    def ready(self):
        print('Ready')
        from django_sendgrid_tracking import signals