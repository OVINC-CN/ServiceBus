import os
from pathlib import Path

from core.logger import get_logging_config_dict
from core.utils import getenv_or_raise, strtobool

# Base Dir
BASE_DIR = Path(__file__).resolve().parent.parent

# Env
try:
    with open(os.path.join(BASE_DIR, "env"), encoding="utf-8") as env_setting_file:
        while True:
            env_setting = env_setting_file.readline()
            if env_setting:
                key, val = env_setting.strip("\n").split("=", 1)
                os.environ[key] = val
            else:
                break
except FileNotFoundError:
    pass

# DEBUG
DEBUG = strtobool(os.getenv("DEBUG", "False"))

# APP_CODE & SECRET
APP_CODE = getenv_or_raise("APP_CODE")
APP_SECRET = getenv_or_raise("APP_SECRET")
SECRET_KEY = getenv_or_raise("APP_SECRET")

# Hosts
ALLOWED_HOSTS = [getenv_or_raise("BACKEND_HOST")]
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", True)
CORS_ORIGIN_WHITELIST = [getenv_or_raise("FRONTEND_URL")]
CSRF_TRUSTED_ORIGINS = [getenv_or_raise("FRONTEND_URL")]
FRONTEND_URL = getenv_or_raise("FRONTEND_URL")

# APPs
INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.account",
    "apps.application",
    "apps.cel",
    "apps.home",
    "apps.iam",
    "apps.notice",
    "apps.trace",
]

# MIDDLEWARE
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "core.middlewares.CSRFExemptMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "core.middlewares.SQLDebugMiddleware",
]
if DEBUG:
    MIDDLEWARE += ["pyinstrument.middleware.ProfilerMiddleware"]
    PYINSTRUMENT_PROFILE_DIR = ".report"
if not DEBUG:
    MIDDLEWARE += ["core.middlewares.UnHandleExceptionMiddleware"]

# Urls
ROOT_URLCONF = "entry.urls"

# TEMPLATES
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = "entry.wsgi.application"

# DB and Cache
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": getenv_or_raise("DB_NAME"),
        "USER": getenv_or_raise("DB_USER"),
        "PASSWORD": getenv_or_raise("DB_PASSWORD"),
        "HOST": getenv_or_raise("DB_HOST"),
        "PORT": int(getenv_or_raise("DB_PORT")),
        "OPTIONS": {"charset": "utf8mb4"},
        "CONN_MAX_AGE": 0 if DEBUG else int(os.getenv("DB_CONN_MAX_AGE", 3600)),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REDIS_HOST = getenv_or_raise("REDIS_HOST")
REDIS_PORT = int(getenv_or_raise("REDIS_PORT"))
REDIS_PASSWORD = getenv_or_raise("REDIS_PASSWORD")
REDIS_DB = int(getenv_or_raise("REDIS_DB"))
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    }
}

# Auth
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# International
LANGUAGE_CODE = os.getenv("DEFAULT_LANGUAGE", "zh-hans")
TIME_ZONE = os.getenv("DEFAULT_TIME_ZONE", "Asia/Shanghai")
USE_I18N = True
USE_L10N = True
USE_TZ = False
LANGUAGES = (("zh-hans", "中文简体"), ("en", "English"))
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

# Static
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "staticfiles")]

# Session
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", f"{'dev-' if DEBUG else ''}{APP_CODE}-sessionid")
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
AUTH_TOKEN_NAME = os.getenv("AUTH_TOKEN_NAME", f"{'dev-' if DEBUG else ''}{APP_CODE}-auth-token")

# Log
LOG_LEVEL = "INFO"
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOGGING = get_logging_config_dict(LOG_LEVEL, LOG_DIR)

# rest_framework
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["core.renderers.APIRenderer"],
    "DEFAULT_PAGINATION_CLASS": "core.paginations.NumPagination",
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DEFAULT_THROTTLE_RATES": {},
    "EXCEPTION_HANDLER": "core.exceptions.exception_handler",
    "UNAUTHENTICATED_USER": "apps.account.models.CustomAnonymousUser",
    "DEFAULT_AUTHENTICATION_CLASSES": ["core.auth.SessionAuthenticate", "core.auth.AuthTokenAuthenticate"],
}

# User
AUTH_USER_MODEL = "account.User"
AUTHENTICATION_BACKENDS = ["apps.account.backends.ModelBackend", "apps.account.backends.TokenBackend"]

# App
# enable will spend extra time at app request
ENCRYPT_APP_SECRET = strtobool(os.getenv("ENCRYPT_APP_SECRET", "False"))

# Celery
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_ENABLE_UTC = False
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ["pickle", "json"]
BROKER_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# APM
ENABLE_TRACE = strtobool(os.getenv("ENABLE_TRACE", "True"))
JAEGER_HOST = os.getenv("JAEGER_HOST", "localhost")
JAEGER_PORT = int(os.getenv("JAEGER_PORT", "6831"))
SERVICE_NAME = os.getenv("SERVICE_NAME", APP_CODE)

# Notice
NOTICE_MAIL_HOST = os.getenv("NOTICE_MAIL_HOST")
NOTICE_MAIL_PORT = int(os.getenv("NOTICE_MAIL_PORT", 465))
NOTICE_MAIL_USERNAME = os.getenv("NOTICE_MAIL_USERNAME")
NOTICE_MAIL_PASSWORD = os.getenv("NOTICE_MAIL_PASSWORD")
NOTICE_MSG_TCLOUD_ID = os.getenv("NOTICE_MSG_TCLOUD_ID")
NOTICE_MSG_TCLOUD_KEY = os.getenv("NOTICE_MSG_TCLOUD_KEY")
NOTICE_MSG_TCLUD_REGION = os.getenv("NOTICE_MSG_TCLUD_REGION", "ap-guangzhou")
NOTICE_MSG_TCLOUD_APP = os.getenv("NOTICE_MSG_TCLOUD_APP")
NOTICE_MSG_TCLOUD_SIGN = os.getenv("NOTICE_MSG_TCLOUD_SIGN")
