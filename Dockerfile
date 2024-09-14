FROM python:3.9-slim

WORKDIR /workdir

COPY requirements.txt /workdir/

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /workdir/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
