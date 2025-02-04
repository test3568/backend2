from pathlib import Path

from config import Config

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = Config.DJANGO_DEBUG
SECRET_KEY = Config.DJANGO_SECRET_KEY

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'polygons.apps.PolygonsConfig',
    'app.apps.AppConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

ROOT_URLCONF = 'backend2.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': Config.POSTGIS_USER,
        'PASSWORD': Config.POSTGIS_PASSWORD,
        'HOST': Config.POSTGIS_HOST,
        'PORT': Config.POSTGIS_PORT,
        'OPTIONS': {
            'pool': True,
        },
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ASGI_APPLICATION = 'backend2.asgi.application'

AUTH_USER_MODEL = 'polygons.User'

GDAL_LIBRARY_PATH=Config.GDAL_LIBRARY_PATH
GEOS_LIBRARY_PATH=Config.GEOS_LIBRARY_PATH

CACHE_POLYGONS_GET_KEY = "polygons_get"
CACHE_INTERSECTIONS_GET_KEY = "intersections_get"
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

KAFKA_SERVER = f'{Config.KAFKA_HOST}:{Config.KAFKA_PORT}'
KAFKA_CONSUMER_TOPIC = Config.KAFKA_CONSUMER_TOPIC
KAFKA_PRODUCER_TOPIC = Config.KAFKA_PRODUCER_TOPIC

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'custom': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s %(asctime)s - %(message)s',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'custom',
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": Config.DJANGO_LOG_LEVEL,
            "propagate": False,
        },
        'app': {
            'handlers': ['console'],
            'level': Config.APP_LOG_LEVEL,
            'propagate': False,
        }
    }
}
