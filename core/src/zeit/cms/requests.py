import signal
import requests


class SignalTimeout(Exception):
    pass


def _handle_timeout(signum, frame):
    raise SignalTimeout()


def request_with_timeout(self, method, url, **kw):
    """The requests library does not allow to specify a duration within which
    a request has to return a response. You can only limit the time to
    wait for the connection to be established or the first byte to be sent,
    but not until the whole response has been sent.
    This uses SIGALRM to enforce a hard timeout on the whole operation.
    """

    try:
        # Timeout tuples (connect, read) shall not invoke signal timeouts
        sig_timeout = float(kw['timeout'])
        # Handler registration fails if it's attempted in a worker thread
        signal.signal(signal.SIGALRM, _handle_timeout)
    except (KeyError, TypeError, ValueError):
        sig_timeout = None
    else:
        signal.setitimer(signal.ITIMER_REAL, sig_timeout)

    try:
        return self._old_request(method, url, **kw)
    except SignalTimeout:
        raise requests.exceptions.Timeout(
            'Request attempt timed out after %s seconds' % sig_timeout
        )
    finally:
        if sig_timeout:
            signal.setitimer(signal.ITIMER_REAL, 0)


def dump_request(response):
    """Debug helper. Pass a `requests` response and receive an executable curl
    command line.
    """
    request = response.request
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = request.method
    uri = request.url
    data = request.body
    headers = ["'{0}: {1}'".format(k, v) for k, v in request.headers.items()]
    headers = ' -H '.join(headers)
    return command.format(method=method, headers=headers, data=data, uri=uri)
