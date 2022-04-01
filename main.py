from celery import group
from fastapi import FastAPI
from opentelemetry.instrumentation.celery import CeleryInstrumentor

import task

app = FastAPI()
CeleryInstrumentor().instrument()


@app.get("/")
async def root():
    return {"message": "I'm Alive!"}


@app.get("/{x}/{y}")
async def add(x, y):
    try:
        _x, _y = int(x), int(y)
    except ValueError:
        return {"error": "input must be integer"}

    if (_x, _y) != (float(x), float(y)):
        return {"error": "input must be integer"}

    result = task.add.delay(_x, _y)

    futures = group(
        task.app.signature(
            "task.add", args=(_x, _y)
        )
        for _ in range(10)
    ).apply_async()

    result = futures.get(timeout=2)
    return {"message": {"result": result}}
