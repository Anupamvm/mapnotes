FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/base.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

EXPOSE 8002
CMD ["gunicorn", "mapnotes.wsgi:application", "--bind", "0.0.0.0:8002", "--workers", "3", "--timeout", "120"]
