import json
import datetime
import logging

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import get_storage_class
from django.http import HttpResponse
from django.conf import settings

from django_sendgrid_tracking.models import SG_EVENTS, SendGridNotification, Mail, MailCategory

logger = logging.getLogger(__name__)

VALID_EVENTS = [x[0] for x in SG_EVENTS]


def get_x_message_id(sg_message_id):
    return sg_message_id.split('.')[0]


def process_sg_notification(sg_notification, file_name):
    try:
        if sg_notification['event'] not in VALID_EVENTS:
            logger.info("Skipping sg_notification processing event type (%s) not in list" % sg_notification['event'])
            return
        if Mail.objects.filter(mail=sg_notification['email'], is_staff=True).exists():
            logger.info("Skipping sg_notification processing mail (%s) not in list" % sg_notification['email'])
            return

        sn = SendGridNotification.objects.create(email=Mail.objects.get_or_create(mail=sg_notification['email'])[0],
                                                 timestamp=sg_notification['timestamp'],
                                                 event_code=sg_notification['event'],
                                                 x_message_id=get_x_message_id(sg_notification['sg_message_id']),
                                                 sg_message_id=sg_notification['sg_message_id'])
        if 'category' in sg_notification:
            if type(sg_notification['category']) is not list:
                sg_notification['category'] = [sg_notification['category']]
            sn.category_code.set(MailCategory.objects.filter(category_code__in=sg_notification['category']))
        else:
            logger.warning('No category in django_sendgrid_tracking:event_hooks, '
                           'Raw message content at: %s' % (
                               file_name if file_name else '(message not dumped you need to set DATALAKE_STORAGE)')
                           )

    except Exception as e:
        logger.error('Generic exception raised in django_sendgrid_tracking:event_hooks (%s) '
                     'Raw message content at: %s' % (
                         e, file_name if file_name else '(message not dumped you need to set DATALAKE_STORAGE)')
                     )


def dump_raw_message_to_storage(body):
    datalake_storage_class = getattr(settings, 'DATALAKE_STORAGE', None)
    if datalake_storage_class:
        datalake_storage = get_storage_class(import_path=settings.DATALAKE_STORAGE)()
        file_name = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f") + '.json'
        file = datalake_storage.open(file_name, 'wb')
        file.write(body)
        file.close()
        logger.debug('Saved message at: %s' % file_name)
        return file_name
    else:
        logger.debug('Raw message not saved')
        return None


@csrf_exempt
@require_POST
def event_hooks(request):
    if request.method == 'POST':
        logger.info('Received Sendgrid Hook request, processing event')
        # After save on datalake process event
        file_name = dump_raw_message_to_storage(request.body)
        sg_notifications = json.loads(request.body)
        if type(sg_notifications) is not list:
            sg_notifications = [sg_notifications]

        for sg_notification in sg_notifications:
            # In case of one events has an error it allows to save other events
            with transaction.atomic():
                process_sg_notification(sg_notification, file_name)
    return HttpResponse()
