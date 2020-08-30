import logging
from collections import Iterable

from django_sendgrid_tracking.models import SentMail, Mail, MailCategory

logger = logging.getLogger(__name__)


def create_send_email(sender, message, fail_flag, **kwargs):
    x_message_id = message.extra_headers.get('message_id', None)
    sent_mail = SentMail.objects.create(
        x_message_id=x_message_id,
        fail_flag=fail_flag
    )
    sent_mail.to_email.set([Mail.objects.get_or_create(mail=mail)[0] for mail in message.to])
    sent_mail.cc_email.set([Mail.objects.get_or_create(mail=mail)[0] for mail in message.cc])
    sent_mail.bcc_email.set([Mail.objects.get_or_create(mail=mail)[0] for mail in message.bcc])

    categories = getattr(message, "categories", None)
    if categories:
        if not isinstance(categories, Iterable):
            logger.warning('Categories field is not iterable (%s)' % categories)
            return
        for category in categories:
            sent_mail.category_code.add(MailCategory.objects.get_or_create(category_code=category)[0])
