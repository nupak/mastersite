# mastersite
Для деплоя

Установить виртуальной окружение с версией python 3.8+
venv/bin/activate
-Все необходимые модули в файле requirements.txt pip freeze -r requirements.txt

-Настройки названия сайта и находятся в папке 
scientistSite -> settings.py
SITE_NAME = 'https://домен_сайта'

ALLOWED_HOSTS = [SITE_NAME]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
      'http://localhost:3000',
        'http://localhost:8000',
        'http://165.22.27.247:8000',
        'http://165.22.27.247:3000',
]

-Запуск сервера Для запуска в режиме теста/продакшн : DEBUG = TRUE/FALSE

-Настройки пользователя базы данных Postgress находятся той же папке
scientistSete -> settings.py

DB_NAME = ""
DB_USER = ""
DB_PASSWORD = ""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

-Запуск локального сервера для проверки после клонирования с репозитории(по умолчанию localhost:8000) python3 manage.py runserver

-На сервере через wsgi через unicorn
В папке проекта scientistSite:
gunicorn --bind 0.0.0.0:8000 scientistSite.wsgi

-Если ошибка запуска юникорн, то запустить
lsof -i:8000
Остановить процессы на порте
kill -9 id_proces




