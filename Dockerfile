FROM python:3.12-slim

COPY . /app
WORKDIR /app

EXPOSE 5000

RUN pip install pipenv && pipenv install --system --deploy

CMD ["python", "app.py"]