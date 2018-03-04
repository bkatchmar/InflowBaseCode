"""
Django settings for inflowhq project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "7t=&8c9%(9%piw_q%pqr_5gis*4dy1^=z47=e+x-uzjv6m!5+e"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost","inflowwinstondev-env.9erc4v9sv4.us-east-2.elasticbeanstalk.com", "workinflow.co"]
ADMINS = [("Brian", "brian@workinflow.co"),]

# Stripe Information
STRIPE_TEST_API_SECRET = "sk_test_ZNyeY1kgGqIgitBn16rLqGNn"
STRIPE_TEST_PUBLISHABLE_KEY = "pk_test_1jY0jXXrP4ov94DS1A1Ndfjp"

# LinkedIn Info
LINKEDIN_CLIENT_ID = "78ikt1qlinvfqg"
LINKEDIN_CLIENT_SECRET = "JxqIUYwOl3BbEDGz"
LINKEDIN_CALL_STATE = "BKlSbtptlh4m0HelllSbhhkHfmt1YasiktH"
LINKEDIN_REDIRECT_URL = "http://inflowwinstondev-env.9erc4v9sv4.us-east-2.elasticbeanstalk.com/"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'inflowco',
    'accounts',
    'contractsandprojects',
    'talktostripe',
    'inflowdemo',
    'easy_pdf'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inflowhq.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inflowhq.wsgi.application'

SILENCED_SYSTEM_CHECKS = ["fields.W342"]

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': { 
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'brianpersonal',
        'USER': 'root',
        'PASSWORD': 'th3l10nk1ng',
        'HOST': 'localhost',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/static/"
LOGIN_URL = "/"

EMAIL_HOST= "email-smtp.us-east-1.amazonaws.com"
EMAIL_HOST_USER = "AKIAI6OO52H7X6ZFGGTQ"
EMAIL_HOST_PASSWORD = "AqH6PVBIqsK2I3+sOwtB99YpRteS0NWB/X0tH/1BdWsD"
EMAIL_USE_TLS = True
SERVER_EMAIL = "brian@workinflow.co"