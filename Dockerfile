FROM python:3

COPY /app/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD [ "python", "./app.py" ]
