from django.apps import AppConfig


class DjangoSendgridEmailConfig(AppConfig):
    name = 'django_sendgrid_tracking'

    def ready(self):
        from django_sendgrid_tracking import signals
        print('Imported %s' % signals.__name__)
