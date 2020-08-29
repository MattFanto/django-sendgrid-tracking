import json

from django.test import TestCase
from django.test import Client
from django.urls import reverse

from django_sendgrid_tracking import views

from django_sendgrid_tracking.models import SendGridNotification, SentMail, Mail, MailCategory


class SendgridWebHookTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.data = [
            {
                "category": [
                    "test",
                    "test.test1",
                    "test.test1.test2"
                ],
                "email": "invited_1@test.com",
                "event": "processed",
                "sg_event_id": "1Lum89GsRMa_20ZONQPNHA",
                "sg_message_id": "aIhbvfvSQIOnDB4e1__0GA.filter0094p3mdw1-7354-5C609188-24.1",
                "smtp-id": "<aIhbvfvSQIOnDB4e1__0GA@ismtpd0006p1lon1.sendgrid.net>",
                "timestamp": 1549832585
            },
            {
                "email": "staff@test.com",
                "timestamp": 1549832644,
                "ip": "93.146.38.232",
                "sg_event_id": "5Fb7pZqjTBGNxtnDL7WIaQ",
                "sg_message_id": "3JXyvYCMTEefIygBw6SSOA.filter0155p3mdw1-2838-5C608EC1-18.0",
                "category": [
                    "test",
                    "test.test1",
                    "test.test1.test2"
                ],
                "useragent": "Microsoft Office/16.0 (Microsoft Outlook 16.0.11029; Pro)",
                "event": "open"
            }
        ]

    def test_bad_input(self):
        client = Client()
        self.assertRaises(TypeError,
                          lambda x: client.generic('POST', reverse(views.event_hooks), json.dumps('[]')))
        self.assertRaises(TypeError,
                          lambda x: client.generic('POST', reverse(views.event_hooks), json.dumps('{}')))

    def test_sg_notification_hook(self):
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        sm2 = SentMail.objects.create(x_message_id='3JXyvYCMTEefIygBw6SSOA')
        data = self.data
        client = Client()

        client.generic('POST', reverse(views.event_hooks), json.dumps(data))

        qs = SendGridNotification.objects.filter(sg_message_id=data[0]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm1)

        qs = SendGridNotification.objects.filter(sg_message_id=data[1]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm2)

    def test_skip_staff_email_notification(self):
        staff_mail = Mail.objects.create(mail='staff@test.com', is_staff=True)
        mail = Mail.objects.create(mail='invited_1@test.com', is_staff=False)
        data = self.data

        client = Client()
        client.generic('POST', reverse(views.event_hooks), json.dumps(data))

        qs = SendGridNotification.objects.filter(email=mail)
        self.assertEqual(qs.count(), 1)
        qs = SendGridNotification.objects.filter(sg_message_id=data[0]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        qs = SendGridNotification.objects.filter(email=staff_mail)
        self.assertEqual(qs.count(), 0)
        qs = SendGridNotification.objects.filter(sg_message_id=data[1]['sg_message_id'])
        self.assertEqual(qs.count(), 0)

        # Also unknown email are saved
        data = self.data.copy()
        data[0]['email'] = 'invited_unkown1@test.com'
        data[0]['sg_message_id'] = 'XXXaIhbvfvSQIOnDB4e1__0GA.filter0094p3mdw1-7354-5C609188-24.1'
        data[1]['email'] = 'invited_unkown2@test.com'
        data[1]['sg_message_id'] = 'XXX3JXyvYCMTEefIygBw6SSOA.filter0155p3mdw1-2838-5C608EC1-18.0'

        client = Client()
        client.generic('POST', reverse(views.event_hooks), json.dumps(data))

        qs = SendGridNotification.objects.filter(sg_message_id=data[0]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        qs = SendGridNotification.objects.filter(sg_message_id=data[1]['sg_message_id'])
        self.assertEqual(qs.count(), 1)

    def test_category_tree(self):
        category_tree = [MailCategory.objects.create(category_code='test', category_descr='test'),
                         MailCategory.objects.create(category_code='test.test1', category_descr='test'),
                         MailCategory.objects.create(category_code='test.test1.test2', category_descr='test')]

        for x, y in zip(category_tree[-1].get_category_tree(), category_tree):
            self.assertEqual(x, y)

    def test_single_event(self):
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        data = self.data
        client = Client()
        self.assertRaises(TypeError,
                          lambda x: client.generic('POST', reverse(views.event_hooks), json.dumps('[]')))
        self.assertRaises(TypeError,
                          lambda x: client.generic('POST', reverse(views.event_hooks), json.dumps('{}')))

        client.generic('POST', reverse(views.event_hooks), json.dumps(data[0]))

        qs = SendGridNotification.objects.filter(sg_message_id=data[0]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm1)

    def test_manage_bad_event(self):
        """
        One event is not correct but the other are processed
        """
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        sm2 = SentMail.objects.create(x_message_id='3JXyvYCMTEefIygBw6SSOA')
        data = self.data.copy()
        data[0]['timestamp'] = 'BAD_TIMESTAMP'
        client = Client()

        client.generic('POST', reverse(views.event_hooks), json.dumps(data))

        qs = SendGridNotification.objects.filter(sg_message_id=data[0]['sg_message_id'])
        self.assertEqual(qs.count(), 0) # not processed

        # The second one should be processed
        qs = SendGridNotification.objects.filter(sg_message_id=data[1]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm2)

    def test_manage_no_category(self):
        """
        One event is not correct but the other are processed
        """
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        sm2 = SentMail.objects.create(x_message_id='3JXyvYCMTEefIygBw6SSOA')
        data = self.data.copy()
        data[0].pop('category')
        client = Client()

        client.generic('POST', reverse(views.event_hooks), json.dumps(data))

        qs = SendGridNotification.objects.filter(sg_message_id=data[0]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm1)

        qs = SendGridNotification.objects.filter(sg_message_id=data[1]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm2)

    def test_not_valid_events(self):
        """
        One event is not correct but the other are processed
        """
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        sm2 = SentMail.objects.create(x_message_id='3JXyvYCMTEefIygBw6SSOA')
        data = self.data.copy()
        data[0]['event'] = 'NOT_VALID'
        client = Client()

        client.generic('POST', reverse(views.event_hooks), json.dumps(data))

        qs = SendGridNotification.objects.filter(sg_message_id=data[0]['sg_message_id'])
        self.assertEqual(qs.count(), 0)

        qs = SendGridNotification.objects.filter(sg_message_id=data[1]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm2)

    def test_single_category(self):
        """
        One event is not correct but the other are processed
        """
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        sm2 = SentMail.objects.create(x_message_id='3JXyvYCMTEefIygBw6SSOA')
        data = self.data.copy()
        data[0]['category'] = 'test'
        client = Client()

        client.generic('POST', reverse(views.event_hooks), json.dumps(data))

        qs = SendGridNotification.objects.filter(sg_message_id=data[0]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm1)

        qs = SendGridNotification.objects.filter(sg_message_id=data[1]['sg_message_id'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().sent_mail, sm2)


class SendgridTrackingTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.data = [
            {
                "category": [
                    "test",
                    "test.test1",
                    "test.test1.test2"
                ],
                "email": "invited_1@test.com",
                "event": "processed",
                "sg_event_id": "1Lum89GsRMa_20ZONQPNHA",
                "sg_message_id": "aIhbvfvSQIOnDB4e1__0GA.filter0094p3mdw1-7354-5C609188-24.1",
                "smtp-id": "<aIhbvfvSQIOnDB4e1__0GA@ismtpd0006p1lon1.sendgrid.net>",
                "timestamp": 1549832585
            },
            {
                "email": "staff@test.com",
                "timestamp": 1549832644,
                "ip": "93.146.38.232",
                "sg_event_id": "5Fb7pZqjTBGNxtnDL7WIaQ",
                "sg_message_id": "3JXyvYCMTEefIygBw6SSOA.filter0155p3mdw1-2838-5C608EC1-18.0",
                "category": [
                    "test",
                    "test.test1",
                    "test.test1.test2"
                ],
                "useragent": "Microsoft Office/16.0 (Microsoft Outlook 16.0.11029; Pro)",
                "event": "open"
            }
        ]
        self.client = Client()

    def test_delivered_flag_and_date(self):
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        # No notification yet
        self.assertFalse(sm1.delivered_flag)
        self.assertIsNone(sm1.delivered_date)

        data = self.data[0].copy()
        data['event'] = 'delivered'
        data['timestamp'] += 10
        self.client.generic('POST', reverse(views.event_hooks), json.dumps(data))
        self.assertTrue(sm1.delivered_flag)
        self.assertEqual(sm1.delivered_date.timestamp(), data['timestamp'])

        # Test updating the last delivered date
        data = self.data[0].copy()
        data['event'] = 'delivered'
        data['timestamp'] += 20
        self.client.generic('POST', reverse(views.event_hooks), json.dumps(data))
        self.assertTrue(sm1.delivered_flag)
        self.assertEqual(sm1.delivered_date.timestamp(), data['timestamp'])

    def test_open_flag_and_date(self):
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        # No notification yet
        self.assertFalse(sm1.open_flag)
        self.assertIsNone(sm1.open_date)

        data = self.data[0].copy()
        data['event'] = 'open'
        data['timestamp'] += 20
        self.client.generic('POST', reverse(views.event_hooks), json.dumps(data))
        self.assertTrue(sm1.open_flag)
        self.assertEqual(sm1.open_date.timestamp(), data['timestamp'])
        # Test updating last open date
        data = self.data[0].copy()
        data['event'] = 'open'
        data['timestamp'] += 30
        self.client.generic('POST', reverse(views.event_hooks), json.dumps(data))
        self.assertTrue(sm1.open_flag)
        self.assertEqual(sm1.open_date.timestamp(), data['timestamp'])

    def test_click_flag_and_date(self):
        sm1 = SentMail.objects.create(x_message_id='aIhbvfvSQIOnDB4e1__0GA')
        # No notification yet
        self.assertFalse(sm1.click_flag)
        self.assertIsNone(sm1.click_date)

        data = self.data[0].copy()
        data['event'] = 'click'
        data['timestamp'] += 30
        self.client.generic('POST', reverse(views.event_hooks), json.dumps(data))
        self.assertTrue(sm1.click_flag)
        self.assertEqual(sm1.click_date.timestamp(), data['timestamp'])
        # Test updating last open date
        data = self.data[0].copy()
        data['event'] = 'click'
        data['timestamp'] += 40
        self.client.generic('POST', reverse(views.event_hooks), json.dumps(data))
        self.assertTrue(sm1.click_flag)
        self.assertEqual(sm1.click_date.timestamp(), data['timestamp'])