from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django_sendgrid_tracking import models
from django_sendgrid_tracking.mail import SendGridEmailMessage


@csrf_exempt
@require_POST
def send_mail(request):
    # sendgrid_email_sent.connect(create_send_email)
    if request.method == 'POST':
        # mail_category = models.MailCategory.objects.create(
        #     category_code='test',
        #     category_descr='test',
        # )
        # models.MailTemplate.objects.create(
        #     type=models.MailTemplate.TYPE_TEXT_PLAIN,
        #     category_code=mail_category,
        #     subject='Hello {{ firstName }}',
        #     body='Welcome to {{ websiteName }}, access here {{ link_url }}',
        #     template_version='v0.1',
        #     sg_template_id='test'
        # )
        msg = SendGridEmailMessage(template_data={
            'firstName': 'user',
            'websiteName': 'here',
            'link_url': 'http://here.com'},
            to=['test@test.com'], cc=[], bcc=[], category_code='test')
        msg.send()

    return HttpResponse()