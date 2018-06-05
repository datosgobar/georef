"""
Django settings for georef project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/
DEBUG = os.environ.get('DEBUG')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_extensions',
    'geo_admin',
]

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

GEOREF = {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': os.environ.get('GEOREF_DB_NAME'),
    'USER': os.environ.get('GEOREF_DB_USER'),
    'PASSWORD': os.environ.get('GEOREF_DB_PASS'),
    'HOST': os.environ.get('GEOREF_DB_HOST'),
    'PORT': '5432',
}

DATABASES = {'default': GEOREF}

EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

EMAIL_REPORT_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS')
EMAIL_REPORT_FROM = 'datos@modernizacion.gobar'
EMAIL_REPORT_SUBJECT = 'GEOREF ETL – Reporte de entidades'
PATH_REPORT_FILE = 'logs/entities_report.json'

TIME_ZONE = 'America/Argentina/Buenos_Aires'
