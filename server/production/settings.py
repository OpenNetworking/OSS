import os

from diqi_oss.settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = False

ROOT_URLCONF = 'urls'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '<your secret key>'

ALLOWED_HOSTS = ['*']


INSTALLED_APPS += [
    # Uncomment the module you wish to use.
    # 'diqi_oss.base',
    # 'diqi_oss.explorer',
]

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'explorer_db': {
        'NAME': 'explorer_db',
        'ENGINE': 'django.db.backends.mysql',
        'USER': '',
        'PASSWORD': ''
    }
}

# Logger

LOG_DIR = '/var/log/diqi_oss'

LOGGING = {
    'version': 1,
    'handlers': {
        'base_log_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'base.log'),
            'formatter': 'api_format'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'formatter': 'verbose'
        },
    },
    'formatters': {
        'api_format': {
            'format': '%(levelname)s %(asctime)s %(endpoint)s %(message)s'
        },
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'loggers': {
        'base': {
            'handlers': ['base_log_file'],
            'level': 'INFO'
        },
        'notification': {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
    }
}
