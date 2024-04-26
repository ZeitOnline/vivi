from datetime import datetime, timezone
from time import sleep

import pytest


def test_publisher_invalidates_fastly(vivi, http):
    article = '/wirtschaft/2010-01/nightwatch-publish.txt'

    expected = datetime.now().isoformat()

    vivi.set_body(article, expected)
    vivi.publish(article)

    # vivi runs the publisher asynchronously from the API call.
    timeout = 60
    for _ in range(timeout):
        sleep(1)
        r = http(article)
        current = r.text.strip()
        if current == expected:
            break
    else:
        pytest.fail('Expected %s, got %s after %s seconds' % (expected, current, timeout))


@pytest.mark.parametrize(
    'content',
    [
        '/wirtschaft/2010-01/automarkt-usa-deutschland-smart',
        '/2010/01/index',
    ],
)
def test_publisher_updates_metadata(vivi, http, config, content):
    before = datetime.now(timezone.utc)
    sleep(1)

    vivi.publish(content)

    # vivi runs the publisher asynchronously from the API call.
    timeout = 60
    for _ in range(timeout):
        sleep(1)
        r = http(
            config['elasticsearch'],
            json={
                'query': {'bool': {'filter': [{'term': {'url': content}}]}},
                '_source': ['payload.workflow.date_last_published'],
            },
        )
        try:
            hit = r.json()['hits']['hits'][0]['_source']
            current = hit['payload']['workflow']['date_last_published']
            current = datetime.fromisoformat(current)
        except Exception:
            current = datetime.min
        if current > before:
            break
    else:
        pytest.fail('%s did not increase after %s seconds' % (current, timeout))
