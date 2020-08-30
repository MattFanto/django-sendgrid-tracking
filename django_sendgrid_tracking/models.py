from datetime import datetime

from django.db import models


class Mail(models.Model):
    mail = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.mail


class MailCategory(models.Model):
    """
    Mail categories are represented in flat hierarchical structure, delimited with "."
    e.g. webapp.app_name.functionality has the following hierarchy:
        webapp
        webapp.app_name
        webapp.app_name.functionality

    This is useful for filtering and reporting
    """

    category_code = models.CharField(primary_key=True, max_length=500, null=False)
    category_descr = models.CharField(max_length=500, null=False)

    # store_sg_notification_flag = models.BooleanField(default=True)

    def get_category_tree(self):
        """
        Return the category hierarchy
        e.g.
        category_code: webapp.app_name.functionality
        @:return category tree like: [
            "webapp",
            "webapp.app_name",
            "webapp.app_name.functionality"
        ]
        """
        category_tree = []
        tokens = self.category_code.split('.')
        for i in range(1, len(tokens)):
            category_tree.append(MailCategory.objects.get(
                category_code='.'.join(tokens[0:i]))
            )
        category_tree.append(self)
        return category_tree

    def __str__(self):
        return self.category_code


class SentMail(models.Model):
    to_email = models.ManyToManyField(Mail, related_name='+')
    cc_email = models.ManyToManyField(Mail, related_name='+')
    bcc_email = models.ManyToManyField(Mail, related_name='+')

    # TODO field which allows overriding to store mail info

    x_message_id = models.CharField(max_length=1000, null=True, default=None)
    category_code = models.ManyToManyField(MailCategory)

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    fail_flag = models.BooleanField(default=False)

    @property
    def delivered_flag(self):
        """
        Whether the email has been delivered to one of the sender (to_email)
        """
        return self.sendgridnotification_set.filter(event_code='delivered', x_message_id=self.x_message_id).exists()

    @property
    def delivered_date(self):
        """
        Last delivered date based on sendgrid notification
        :return: most recent delivered date
        """
        qs = self.sendgridnotification_set.filter(event_code='delivered', x_message_id=self.x_message_id) \
            .order_by('-timestamp')
        if qs.count() == 0:
            return None
        else:
            return datetime.fromtimestamp(qs.first().timestamp)

    @property
    def open_flag(self):
        """
        Whether one of the sender (to_email) has opened the mail
        """
        return self.sendgridnotification_set.filter(event_code='open', x_message_id=self.x_message_id).exists()

    @property
    def open_date(self):
        """
        Last open date based on sendgrid notification
        :return: most recent open date
        """
        qs = self.sendgridnotification_set.filter(event_code='open', x_message_id=self.x_message_id).order_by(
            '-timestamp')
        if qs.count() == 0:
            return None
        else:
            return datetime.fromtimestamp(qs.first().timestamp)

    @property
    def click_flag(self):
        """
        Whether one of the receiver (to_email) has click on the email link
        """
        return self.sendgridnotification_set.filter(event_code='click', x_message_id=self.x_message_id).exists()

    @property
    def click_date(self):
        """
        Last delivered click based on sendgrid notification
        :return: most recent click date
        """
        qs = self.sendgridnotification_set.filter(event_code='click', x_message_id=self.x_message_id).order_by(
            '-timestamp')
        if qs.count() == 0:
            return None
        else:
            return datetime.fromtimestamp(qs.first().timestamp)


SG_EVENTS = (
    ('processed', 'Message has been received and is ready to be delivered.'),
    ('dropped', 'You may see the following drop reasons: Invalid SMTPAPI header, '
                'Spam Content (if Spam Checker app is enabled), Unsubscribed Address, '
                'Bounced Address, Spam Reporting Address, Invalid, Recipient List over Package Quota'),
    ('delivered', 'Message has been successfully delivered to the receiving server.'),
    ('deferred', 'Receiving server temporarily rejected the message.'),
    ('bounce',
     'Receiving server could not or would not accept the message. '
     'If a recipient has previously unsubscribed from your emails, the message is bounced.'),
    ('open', 'User opened the message'),
    ('click', 'User clicked on the message link'),
    ('spamreport', 'Recipient marked message as spam.')
)


class SendGridNotification(models.Model):
    email = models.ForeignKey(Mail, null=True, on_delete=models.SET_NULL)
    timestamp = models.IntegerField()
    event_code = models.CharField(max_length=200, choices=SG_EVENTS)
    sg_message_id = models.CharField(max_length=200, null=True, blank=True)
    x_message_id = models.CharField(max_length=100, null=True, blank=True)
    category_code = models.ManyToManyField(MailCategory)

    sent_mail = models.ForeignKey(SentMail, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if self.sg_message_id:
            qs = SentMail.objects.extra(where=["%s like x_message_id||'%%'"], params=[self.sg_message_id])
            if qs.count() == 1:
                self.sent_mail = qs.first()
        super().save(*args, **kwargs)
