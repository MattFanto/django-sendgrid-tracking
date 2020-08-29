import io
import os
from setuptools import setup, find_packages

__version__ = None
with open('django_sendgrid_tracking/version.py') as f:
    exec(f.read())

dir_path = os.path.abspath(os.path.dirname(__file__))
long_description = io.open(os.path.join(dir_path, 'README.rst'), encoding='utf-8').read()

setup(
    name='django-sendgrid-tracking',
    version=str(__version__),
    packages=find_packages(exclude=["temp*.py", "test"]),
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
    ],
)
