Django Sendgrid Tracking
========================

|Travis| |codecov| |Python Versions| |PyPI Version| |MIT licensed|


**Sendgrid Mail tracking for Django, store sendgrid tracking info into django models.**

This library allows to track the email sent using Sendgrid by storing information collected from a webhook into django models.

Table of Contents
=================

-  `Installation <#installation>`__
-  `Quick Start <#quick-start>`__
-  `Common Use Cases <#use-cases>`__
-  `About <#about>`__
-  `License <#license>`__

Installation
============

Prerequisites
-------------

- Python version 3.6+
- Sendgrid account and API configuration

Environment Variables
--------------------------

This library uses `django-sendgrid-v5 <https://github.com/sklarsa/django-sendgrid-v5>`__
which requires the following in your `settings.py`:

.. code:: python

    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]

You can find more information and other settings `here <https://github.com/sklarsa/django-sendgrid-v5>`__

Install package
---------------

Install the library with pip

.. code:: bash

    $ pip install django-sendgrid-tracking


Quick Start
===========

Below the steps to start using django-sendgrid-tracking in your django project using your sendgrid account.

Enable django
-------------

To enable django_sendgrid_tracking in your project you to add it to INSTALLED_APPS in your projects settings.py file

.. code:: python

    INSTALLED_APPS = (
        ...
        'django_sendgrid_tracking'
        ...
    )

Run django migrate to create django-sendgrid-tracking related models

.. code:: bash

    $ python manage.py migrate


In addition to that you need to expose for sendgrid the webhook endpoint

.. code:: python

    from django.conf.urls import url
    from django_sendgrid_tracking import views

    ...
    urlpatterns = [
        ...
        url(r'sendgrid_webhook', views.event_hooks, name='sendgrid_webhook'),
        ...
    ]

Enable sendgrid
---------------

Now you need to provide this endpoint URL to Sendgrid from the console
(`Setting -> Mail Settings -> Event WebHook <https://app.sendgrid.com/settings/mail_settings>`__):

.. image:: https://raw.githubusercontent.com/MattFanto/django-sendgrid-tracking/master/docs/img/sendgrid-webhook-conf.png
    :alt: sendgrid-webhook-configuration


In this case your webhook would be available at http://www.mywebsite.com/sendgrid_webhook/
N.B. remember to append a slash at the end of it since it will be a POST request


Use cases
=========

The most simple use case would be to analyse internal statics or troubleshoot pitfall in the application flow.
As an example we can see for which reason a particular user didn't confirm the email address

e.g.

.. code:: python

    sent_email = SentMail.object.filter(
        to_email__mail=user.mail,
        categories__category_code='confirm_email'
    )
    print(sent_email.open_flag)
    # True the user opened the email
    print(sent_email.click_flag)
    # False the user didn't click on the confirmation link
    # Maybe something is wrong with the content of the email?


Another use case is in the case of referral program we can show the user the status of the sent invitation

e.g.

.. image:: https://raw.githubusercontent.com/MattFanto/django-sendgrid-tracking/master/docs/img/use-case-referral.png
    :alt: use-case-referral

(example from https://www.omologherifiuti.it)

About
======

django-sendgrid-tracking is a library extracted from different website implemented by the author in django

If you've instead found a bug in the library or would like new features added, go ahead and open issues or pull requests against this repo!

Any contribution is appreciated!! (see `CONTRIBUTING`_)

License
=======

`The MIT License (MIT)`_


.. _CONTRIBUTING: https://github.com/MattFanto/django-sendgrid-tracking/blob/master/CONTRIBUTING.md
.. _The MIT License (MIT): https://github.com/MattFanto/django-sendgrid-tracking/blob/master/LICENSE.md
.. |Travis| image:: https://travis-ci.org/MattFanto/django-sendgrid-tracking.svg?branch=master
    :target: https://travis-ci.org/MattFanto/django-sendgrid-tracking
.. |codecov| image:: https://codecov.io/gh/MattFanto/django-sendgrid-tracking/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/MattFanto/django-sendgrid-tracking
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/django-sendgrid-tracking.svg
   :target: https://pypi.org/project/django-sendgrid-tracking
.. |PyPI Version| image:: https://img.shields.io/pypi/v/django-sendgrid-tracking.svg
   :target: https://pypi.org/project/django-sendgrid-tracking
.. |MIT licensed| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: ./LICENSE.md