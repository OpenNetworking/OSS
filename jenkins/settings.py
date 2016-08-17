import os

from diqi_oss.settings import *


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*bps21z53b4pxc3!$wb8svsjsvpd4n975ji38q6zbfvtgjjv&%'

ALLOWED_HOSTS = []

INSTALLED_APPS += (
    'diqi_oss.base',
    'diqi_oss.explorer',
    'diqi_oss.notification',
    'django_jenkins',
)

PROJECT_APPS = (
    'diqi_oss.base',
    'diqi_oss.explorer',
    'diqi_oss.notification',
)

JENKINS_TASKS = (
    'django_jenkins.tasks.run_flake8',
    'django_jenkins.tasks.run_pylint',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'explorer_db': {
        'NAME': 'explorer_db',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': ''
    }
}

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

LOG_DIR = os.path.join(BASE_DIR, 'log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'notification': {
            'handlers': ['file'],
            'level': 'DEBUG'
        }
    }
}
