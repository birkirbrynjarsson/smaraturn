FROM python:3.7.1-stretch

COPY . /app
WORKDIR /app

EXPOSE 5000

RUN pip install pipenv && pipenv install --system --deploy

CMD ["python", "app.py"]