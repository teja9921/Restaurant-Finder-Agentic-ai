"""OpenTelemetry observability setup."""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource


def setup_observability() -> None:
    """
    Setup OpenTelemetry  with CloudWatch integration.
    
    Creates traces for agent execution that flow to CloudWatch.
    """

    service_name = os.getenv("OTEL_SERVICE_NAME", "restaurant-finder-api")

    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP exporter only when explicitly enabled and endpoint is set.
    traces_exporter = os.getenv("OTEL_TRACES_EXPORTER", "otlp").lower().strip()
    otlp_endpoint = (
        os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
        or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    )
    if traces_exporter == "otlp" and otlp_endpoint:
        insecure = os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=insecure)
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)
        print(f"[Observability] OTLP tracing enabled -> {otlp_endpoint}")
    else:
        print("[Observability] OTLP tracing disabled (set OTEL_EXPORTER_OTLP_ENDPOINT to enable)")

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    print(f"[Observability] Configured for service: {service_name}")


def get_tracer(name: str = __name__):
    """
    Get tracer instance.

    Args:
        name: Tracer name

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def trace_function(span_name: str):
    """
    Decorator to trace function execution.

    Args:
        span_name: Name for the span

    Returns:
        Decorator function
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name):
                return await func(*args, **kwargs)
        return wrapper
    return decorator
