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
        r = vivi._request(
            'get',
            f'/public/api/v1/resource{content}',
            params={'ns': 'workflow', 'name': 'date_last_published'},
            headers={'accept': 'application/json'},
        )
        try:
            current = r.json()['workflow']['date_last_published']
            current = datetime.fromisoformat(current)
        except Exception:
            current = datetime.min
        if current > before:
            break
    else:
        pytest.fail('%s did not increase after %s seconds' % (current, timeout))


def test_publish_image_works(vivi, config):
    image = '/wirtschaft/2010-01/china-exportschlager'
    job = vivi.publish(image)

    timeout = 60
    for _ in range(timeout):
        sleep(1)
        if vivi.job_status(job) == 'SUCCESS':
            break
    else:
        pytest.fail(
            'Publish returned error after %s seconds:\n%s' % (timeout, vivi.job_result(job))
        )
