"""
Django settings for traceability_system project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import base64
from pathlib import Path
from hfc.fabric import Client
import os

from OpenSSL import crypto

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#############################
#          IMPORTANT        #
#############################
BLOCKCHAIN_LAYER_OPTIONS = ['Fabric', 'Ethereum']
BLOCKCHAIN_LAYER = os.getenv("TRACEABILITY_SYSTEM_BLOCKCHAIN_LAYER",
                             'Fabric')  # Select blockchain layer Fabric/Ethereum (Ethereum WIP)

if BLOCKCHAIN_LAYER not in BLOCKCHAIN_LAYER_OPTIONS:
    raise EnvironmentError("{} its invalid option please set TRACEABILITY_SYSTEM_BLOCKCHAIN_LAYER"
                           " variable with crrect option, options: {}".format(BLOCKCHAIN_LAYER,
                                                                              str(BLOCKCHAIN_LAYER_OPTIONS)))

                                                                              # Quick-start development settings - unsuitable for production

ORGS = ["org1.example.com", "org2.example.com"]
FABRIC_USER = os.getenv("TRACEABILITY_FABRIC_USER", "User1")
FABRIC_ORG = int(os.getenv("TRACEABILITY_FABRIC_ORG", "1")) # 1 o 2
FABRIC_NET_PROFILE = "./FabricContainerSetup/network.json"
FABRIC_CLIENT = Client(net_profile=FABRIC_NET_PROFILE)
FABRIC_CLIENT.new_channel('mychannel')

# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('TRACEABILITY_SYSTEM_SECRET_KEY',
                       'django-insecure-*+-!%aq=)+bu(8sj4)wfc0vfr4#=^sfu%&%z2=(c68fz%@7@)j')
# SECURITY WARNING: don't run with debug turned on in production!
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv('TRACEABILITY_SYSTEM_DEBUG', 'True') == 'True' else False

ALLOWED_HOSTS = ['*']

API_URL = os.getenv('TRACEABILITY_SYSTEM_API_URL', 'http://localhost:8000')

# Application definition

INSTALLED_APPS = [
    "frontend.apps.FrontendConfig",
    "api.apps.ApiConfig",
    "fabric.apps.FabricConfig",
    "core.apps.CoreConfig",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
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

ROOT_URLCONF = 'traceability_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

ASGI_APPLICATION = 'traceability_system.asgi.application'



def get_identity(cert_data: str) -> str:
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
    # Get cert subject
    subject = certificate.get_subject()

    # Extract the subjects components
    common_name = subject.CN
    organizational_unit = subject.OU
    locality = subject.L
    state = subject.ST
    country = subject.C

    # Build cert identity
    identity = f"x509::CN={common_name},OU={organizational_unit},L={locality},ST={state},C={country}::"

    # Get cert issuer
    issuer = certificate.get_issuer()

    # Extract cert issuer
    issuer_common_name = issuer.CN
    issuer_organization = issuer.O
    issuer_locality = issuer.L
    issuer_state = issuer.ST
    issuer_country = issuer.C

    # Add emiter id to the cet id
    identity += f"CN={issuer_common_name},O={issuer_organization},L={issuer_locality},ST={issuer_state},C={issuer_country}"
    #return identity
    return str(base64.b64encode(identity.encode('utf-8')).decode('utf-8'))



OWNER_IDENTITY = get_identity(FABRIC_CLIENT.get_user(org_name=ORGS[FABRIC_ORG-1], name=FABRIC_USER).enrollment._cert)
print(OWNER_IDENTITY)

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

POSTGRES_NAME = os.getenv("POSTGRES_NAME", '')
POSTGRES_USER = os.getenv("POSTGRES_USER", '')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", '')
POSTGRES_HOST = os.getenv("POSTGRES_HOST", 'db')

if POSTGRES_USER:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_NAME'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': POSTGRES_HOST,
            'PORT': 5432,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
