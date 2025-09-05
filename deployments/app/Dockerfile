FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && rm requirements.txt
COPY /backend /app/backend

CMD ["python", "-m", "backend.app"]
