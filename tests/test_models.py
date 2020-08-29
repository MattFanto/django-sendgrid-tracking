import json

from django.test import TestCase
from django.test import Client
from django.urls import reverse

from django_sendgrid_tracking import views

from django_sendgrid_tracking.models import SendGridNotification, SentMail, Mail, MailCategory


class ModelTestCase(TestCase):

    def setUp(self):
        super().setUp()

    def test_mail_category(self):
        mc = MailCategory.objects.create(
            category_code='test1.test2',
            category_descr='test1 2 nest'
        )
        self.assertEqual(str(mc), 'test1.test2')
        # self.assertEqual(mc.get_category_tree(), ['test1', 'test2'])

    def test_mail(self):
        mail = Mail.objects.create(mail='test@test.com')
        self.assertEqual(str(mail), 'test@test.com')
