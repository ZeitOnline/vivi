def record_with_requests_bugfix(self, amount, attributes=None):
    if self._metric._name == 'http_client_duration_ms':
        amount /= 1000
    return self._old_record(amount, attributes)
