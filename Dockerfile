FROM python:3.8.5
WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

COPY ./entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN chown root /entrypoint.sh

CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000
ENTRYPOINT ["/entrypoint.sh"]