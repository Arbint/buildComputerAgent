import base64
import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def SetupTracing()->trace.Tracer:
    publicKey = os.environ.get("LANGFUSE_PUBLIC_KEY", default ="Not Found")
    secretKey = os.environ.get("LANGFUSE_SECRET_KEY", default="Not Found")
    host = os.environ.get("LANGFUSE_HOST", "localhost:3000")

    credentials = base64.b64encode(f"{publicKey}:{secretKey}".encode()).decode()
    
    exporter = OTLPSpanExporter(
        endpoint=f"{host}/api/public/otel/v1/traces",
        headers={"Authorization": f"Basic {credentials}"}
    )

    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    return trace.get_tracer("buildComputer")
