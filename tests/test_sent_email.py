from unittest.mock import patch, MagicMock, Mock

from django.core.mail import EmailMessage
from django.test import TestCase, override_settings

from django_sendgrid_tracking.models import SendGridNotification, SentMail, Mail, MailCategory
from tests.settings import EMAIL_BACKEND


class SendgridTestSentEmail(TestCase):

    def setUp(self) -> None:
        self.mail_category = MailCategory.objects.create(
            category_code='test',
            category_descr='test',
        )
        self.to = ['test@test.com']
        self.cc = ['test_cc@test.com', 'test_cc1@test.com']
        self.bcc = ['test_bcc@test.com', 'test_bcc1@test.com']

    def _get_message(self):
        msg = EmailMessage(subject="Hello World", body="Hello World",
                           to=self.to, cc=self.cc, bcc=self.bcc)
        msg.categories = [
            str(self.mail_category)
        ]
        return msg

    def flat_values_list(self, m2m, attr):
        return [x[0] for x in m2m.values_list(attr)]

    @override_settings(EMAIL_BACKEND=EMAIL_BACKEND)
    def test_sent_email_creation(self):
        msg = self._get_message()
        x_message_id = 'aIhbvfvSQIOnDB4e1__0GA'
        resp = Mock()
        resp.headers = {'x-message-id': x_message_id}
        resp.status_code = 202

        client_mock = Mock()
        client_mock.mail.send.post.return_value = resp
        msg.get_connection()
        msg.connection.sg.client = client_mock

        msg.send()

        sent_mail = SentMail.objects.get(x_message_id=x_message_id)
        msg.sent_mail = sent_mail
        self.assertIsNotNone(msg.sent_mail, msg='sent_mail should exists now')
        self.assertEqual(msg.sent_mail.category_code.count(), 1)
        self.assertEqual(msg.sent_mail.category_code.first().category_code, 'test')
        self.assertFalse(msg.sent_mail.fail_flag)
        # self.assertEqual(msg.sent_mail.mail_template, self.mail_template)
        self.assertEqual(msg.sent_mail.x_message_id, x_message_id)
        self.assertListEqual(self.flat_values_list(msg.sent_mail.to_email, 'mail'), self.to)
        self.assertListEqual(self.flat_values_list(msg.sent_mail.cc_email, 'mail'), self.cc)
        self.assertListEqual(self.flat_values_list(msg.sent_mail.bcc_email, 'mail'), self.bcc)

    # TODO check invalid category