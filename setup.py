import os
from distutils.core import setup

long_description = """
django-extensions provides a set of utilities to store in django db model tracking information sent by Sendgrid. 
See the project page for more information:
  https://github.com/MattFanto/django-sendgrid-tracking"""
if os.path.isfile("README.rst"):
    with open("README.rst") as f:
        long_description = f.read()

setup(
    name='django-sendgrid-tracking',
    version='0.1',
    packages=['django_sendgrid_tracking', 'django_sendgrid_tracking.migrations'],
    url='https://github.com/MattFanto/django-sendgrid-tracking',
    license='MIT',
    author='Mattia Fantoni',
    author_email='mattia.fantoni@gmail.com',
    description='Sendgrid Mail tracking for Django, store sendgrid tracking info into django models.',
    long_description=long_description,
    python_requires=">=3.6",
    install_requires=[
        "Django>=1.11",
        "pybars3",
        "django-extensions",
        "django-sendgrid-v5>=0.9.0"
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Email :: Tracking",
        "Topic :: Communications :: Email :: HTML Template",
    ],
)
