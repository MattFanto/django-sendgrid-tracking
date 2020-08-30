import io
import os
import sys

from setuptools import setup, find_packages

from django_sendgrid_tracking import __version__ as version

dir_path = os.path.abspath(os.path.dirname(__file__))
long_description = io.open(os.path.join(dir_path, 'README.rst'), encoding='utf-8').read()

if sys.argv[-1] == 'tag':
    print('Tagging the version on git:')
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system('git push --tags')
    sys.exit()

setup(
    name='django-sendgrid-tracking',
    version=version,
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
