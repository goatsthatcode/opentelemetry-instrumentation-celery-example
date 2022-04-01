import os
from celery import Celery
from celery.signals import worker_process_init

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.celery import CeleryInstrumentor

app = Celery(
    broker=os.environ['BROKER_URL'],
    backend=os.environ['RESULT_BACKEND'],
)


@worker_process_init.connect
def init_worker(**kwargs):
    # Configure the tracer to export traces to Jaeger
    resource = Resource(attributes={
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "worker"),
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))

    otlp_exporter = OTLPSpanExporter(
        endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector:4317"),
        insecure=os.environ.get("OTEL_EXPORTER_OTLP_INSECURE", True),
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    CeleryInstrumentor().instrument()


@app.task
def add(x, y):
    result = x + y
    print(result)
    return result
