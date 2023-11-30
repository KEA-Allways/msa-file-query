FROM python:3.11

COPY . /src
WORKDIR /src

RUN pip install --no-cache-dir --upgrade requirements.txt

CMD ["uvicorn", "main:app", "--host", "3.86.230.148", "--port", "8088"]