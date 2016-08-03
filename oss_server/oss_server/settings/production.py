from .base import *

DEBUG = False

INSTALLED_APPS += [
    'base',
]

ALLOWED_HOSTS = ['*']

# Logger

BASE_MODULE_LOG_DIR = '/opt/oss/log/'

LOGGING = {
    'version': 1,
    'handlers': {
        'base_log_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_MODULE_LOG_DIR + 'base.log',
            'formatter': 'api_format'
        },
        'django_log_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_MODULE_LOG_DIR + 'django.log',
        }
    },
    'formatters': {
        'api_format': {
            'format': '%(levelname)s %(asctime)s %(endpoint)s %(message)s'
        }
    },
    'loggers': {
        'base': {
            'handlers': ['base_log_file'],
            'level': 'INFO'
        },
        'django': {
            'handlers': ['django_log_file'],
            'level': 'INFO'
        }
    }
}
