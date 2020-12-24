FROM python:3.8.6

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . ./

RUN chmod 777 ./startup.sh && \
    sed -i 's/\r//' ./startup.sh

RUN mkdir -p static_back
RUN mkdir -p media_back
# need to wait while db connection will bw established
# RUN python manage.py migrate
RUN python manage.py collectstatic

EXPOSE 8000
EXPOSE 8001

VOLUME /usr/src/app/static_back
VOLUME /usr/src/app/media_back

CMD ["./startup.sh"]


