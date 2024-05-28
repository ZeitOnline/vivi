from prometheus_client import CollectorRegistry, Counter, Gauge, Summary


REGISTRY = CollectorRegistry()
LENGTH = Gauge(
    'vivi_newsimport_api_queue_length', 'count dpa entries / API request', registry=REGISTRY
)
EXECUTION_TIME = Summary(
    'vivi_newsimport_api_duration', 'Execution time processing all dpa entries', registry=REGISTRY
)
COUNT_EXCEPTIONS = Counter(
    'vivi_newsimport_api_counts_exceptions', 'newsimport_api_publish', registry=REGISTRY
)
COUNT_PUBLISH = Counter(
    'vivi_newsimport_api_counts_publish', 'newsimport_api_publish', registry=REGISTRY
)
COUNT_RETRACT = Counter(
    'vivi_newsimport_api_counts_retract', 'newsimport_api_retract', registry=REGISTRY
)
COUNT_PUBLISH_ERROR = Counter(
    'vivi_newsimport_api_counts_publish_error', 'newsimport_api_publish_error', registry=REGISTRY
)
COUNT_RETRACT_ERROR = Counter(
    'vivi_newsimport_api_counts_retract_error', 'newsimport_api_retract_error', registry=REGISTRY
)
