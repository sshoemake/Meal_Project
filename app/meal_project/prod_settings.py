import os 
from .settings import *
from .settings import BASE_DIR


SECRET_KEY = os.environ['SECRET']
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']]
DEBUG = False

conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': conn_str_params['dbname'],
        'USER': conn_str_params['user'],
        'PASSWORD': conn_str_params['password'],
        'HOST': conn_str_params['host'],
        'PORT': '',  # typically blank for Azure
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            # 'encrypt': True, 'TrustServerCertificate': 'yes' as needed
        },
    }
}