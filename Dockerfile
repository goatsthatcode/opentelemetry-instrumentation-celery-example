FROM python:3.8.12-slim

WORKDIR /usr/src/app

RUN pip3 install --upgrade pip

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip3 install --no-cache-dir \
        -r /usr/src/app/requirements.txt &&\
    opentelemetry-bootstrap --action=install

COPY ./ /usr/src/app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--log-level", "critical","--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
