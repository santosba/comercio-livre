FROM python:3.13-slim


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y sudo
 

COPY . .
COPY .env .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]