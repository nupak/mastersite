# Деплой create-react-app + django на Ubuntu server

## Минимальная настройка сервера перед установкой

1. Включить ufw firewall (опционально, но желательно)
2. Настройка ssh доступа по ключам (опционально, для удобства)
3. Создание не root пользователя для работы 

```bash
adduser --ingroup sudo <username>
```

4. Обновление пакетов и установка некоторых базовых утилит

```bash
sudo apt update
sudo apt upgrade
sudo apt install vim screenfetch htop tmux # возможно, достаточно htop, а может и вообще не надо, но я ставлю )
```

## Nginx

1. Установить нгинкс на сервер

```bash
sudo apt install nginx
sudo systemctl start nginx # запустить нгинкс
sudo systemctl enable nginx # автоматически включать нгинкс после ребута
```

2. Конфигурация

Базовый конфиг нгинкса лежит в `/etc/nginx/nginx.conf`. Его трогать не надо.
Добавление своих конфигов лучше делать через директорию `/etc/nginx/conf.d/`, в случае одного домена
будет достаточно одного конфига, например `/etc/nginx/conf.d/default.conf`. Все `*.conf` из этой папки нгинкс добавит автоматически в базовый конфиг.

Вот актуальный конфиг сразу для всего, без лишних заумствований:

```nginx
server {
	server_name allday.rest www.allday.rest;
	
  # Локейшн для фронтенда, просто проксируем на нгинкс всё
	location / {
		proxy_pass http://localhost:5000;	
    			proxy_set_header Host $host; 				
	        proxy_set_header Server $host;				
        	client_max_body_size 10M;
	}

	# Для запросов к вебсокетам
	location ^~ /ws/ {
      proxy_pass http://0.0.0.0:8001;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
  }

	# Нужно для того, чтобы джанга находила статику, иначе не пашет
  location /static_back {
    alias /home/user/backend/prod/static_back;
  }
	
  # Основные локейшны для джанги
  location ^~ /api/v1/ {                    
    proxy_pass http://0.0.0.0:8000/api/v1/;   
          proxy_set_header Host $host; 				
          proxy_set_header Server $host;				
          client_max_body_size 10M;					
  }                                                   
  location ^~ /admin/ {                    
    proxy_pass http://0.0.0.0:8000/admin/;   
          proxy_set_header Host $host; 				
          proxy_set_header Server $host;				
          client_max_body_size 10M;					
  } 													
  location ^~ /login/ {                    
    proxy_pass http://0.0.0.0:8000/login;   
          proxy_set_header Host $host; 				
          proxy_set_header Server $host;			
          client_max_body_size 10M;					
  } 
  location ^~ /login {                    
    proxy_pass http://0.0.0.0:8000/login;   
          proxy_set_header Host $host; 				
          proxy_set_header Server $host;				
          client_max_body_size 10M;					
  } 
  location ^~ /logout {                    
    proxy_pass http://0.0.0.0:8000/logout;  
          proxy_set_header Host $host; 			
          proxy_set_header Server $host;		
          client_max_body_size 10M;	
  } 
  location ^~ /register/ {                    
    proxy_pass http://0.0.0.0:8000/register;   
          proxy_set_header Host $host; 			
          proxy_set_header Server $host;		
          client_max_body_size 10M;					
  } 
  location ^~ /register {             
    proxy_pass http://0.0.0.0:8000/register;   
          proxy_set_header Host $host; 			
          proxy_set_header Server $host;		
          client_max_body_size 10M;	
  }
  
  # Добавляется автоматически Цертботом
  listen 443 ssl; # managed by Certbot
  ssl_certificate /etc/letsencrypt/live/www.allday.rest/fullchain.pem; # managed by Certbot
  ssl_certificate_key /etc/letsencrypt/live/www.allday.rest/privkey.pem; # managed by Certbot
  include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

# Добавляется автоматически Цертботом
server {
    if ($host = www.allday.rest) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
	server_name allday.rest www.allday.rest;
	listen 80;
    return 404; # managed by Certbot
}
```


## Letsencript/ssl/https

[Вот тут можно посмотреть, как скачать и пользоваться цертботом](https://certbot.eff.org/lets-encrypt/ubuntufocal-nginx)

1. Установить
2. Запустить что-то вроде `sudo certbot --nginx`
3. Указать в интерактиве, что просят, выбрать домены для сертификата

Certbot сам сгенерирует то что нужно в конфиге нгинкса.

## Postgresql (локально)

1. Ставим постгрес, врубаем

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

2. Входим в `psql` и настраиваем базу:

```bash

psql -U postgres # вход

# \q  - выйти из psql
# \l  - показать базы
# \du - показать роли

create role django with password 'adminlikeadmin'; 
create database scientist_bd encoding 'UTF-8';
grant all privileges on database scientist_bd to django;
# может нужно будет разрешить роли django логиниться 
\q
```

3. Для настройки доступа к базе из докера, поменяем конфиги и ребутнём постгрес:

```bash
sudo find / -type f -name postgresql.conf
nano .../postgresql.conf
# add line: listen_addresses = '*'
# save
```

```bash
sudo find / -type f -name pg_hba.conf
nano .../pg_hba.conf
# add line: host scientist_bd django 172.17.0.0/16 trust
# save
```

[Инфа отсюда](https://gist.github.com/MauricioMoraes/87d76577babd4e084cba70f63c04b07d)

## Docker (Установка и базовая настройка)

1, [Просто шаг 1 отсюда](https://www.digitalocean.com/community/tutorials/docker-ubuntu-18-04-1-ru)
2. 
~~~bash
sudo systemcl start docker 
sudo systemctl enable docker
~~~

## create-react-app in docker (nginx)

1. Нужно поставить ноду нужной версии

```bash
sudo apt install nodejs npm
sudo npm cache clean -f
sudo npm install -g n
sudo n 15.3.0
sudo npm install -g npm@6.14.8
```

2. Первый запуск проекта с гита

```bash
git clone https://github.com/FSWL98/scientists
mv scientists frontend
cd frontend
chmod +x run.sh
sudo ./run.sh
```

3. При обновлении кода в репозитории, для пересборки: 

```bash
cd frontend
git pull # Можно включить в run.sh и стартовать только его
sudo ./run.sh
```

## django in docker (python, gunicorn)

Не всё делал я, надо бы дополнить, опишу в общих чертах

1. первый запуск с гита
```bash
git clone https://github.com/nupak/mastersite.git
mv mastersite backend
cd backend
mkdir -p {static_back,media_back,static}
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic
chmod +x run.sh
sudo ./run.sh
```

2. после обновления
```bash
cd backend
. venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py collectstatic
sudo ./run.sh
```


