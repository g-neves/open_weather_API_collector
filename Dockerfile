FROM python:3.8-slim-buster
WORKDIR /app
COPY . /app
RUN apt-get update && \
    apt-get install -y gcc && \
    pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
