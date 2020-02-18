DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'LA_ACS_dev',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'la_acs_mysql_container',
        'PORT': '3306',
    }
}

# 'ENGINE': 'django.db.backends.postgresql_psycopg2',
# 'NAME': 'similar_predict',
# 'USER': 'postgres',
# 'PASSWORD': 'root',
# 'HOST': 'localhost',
# 'PORT': '5432',
