from time import sleep

import pytest


def test_intextlink_body(tms):
    # /sport/fussball/2010-01/frings-abschied-kommentar
    article = '{urn:uuid:e4b60068-8877-4f0b-92ef-76be88188e2b}'
    r = tms('/in-text-linked-documents/' + article)
    data = r.json()
    assert data['body'].startswith('<body')


def test_topic_page_documents(tms):
    count = 10
    r = tms('/topic-pages/berlin/documents', params={'rows': count, 'filter': 'topicpage'})
    data = r.json()
    assert len(data['docs']) == count


def test_checkin_updates_nonpublished_index(vivi, tms):
    article = '/wirtschaft/2010-01/arabische-emirate-atomenergie'
    uuid = vivi.get_uuid(article)
    previous = tms(f'/content/{uuid}').json()
    # We change the value and then check that the change was propagated.
    expected = not previous['payload']['document']['comments_premoderate']

    published = tms(f'/content/{uuid}/published').json()
    published = published['payload']['document']['comments_premoderate']

    # Storage API calls vivi invalidate and update_tms implicitly on write,
    # not really a "checkin", but close enough.
    vivi.set_property(article, 'document', 'comments_premoderate', expected)

    # Updating ES is not synchronous
    timeout = 10
    for _ in range(timeout):
        sleep(1)
        current = tms(f'/content/{uuid}').json()
        if current and current['payload']['document']['comments_premoderate'] == expected:
            break
    else:
        pytest.fail(
            'Expected premoderate=%s, got %s after %s seconds'
            % (expected, current['payload']['document']['comments_premoderate'], timeout)
        )

    # Published version has not been changed.
    current = tms(f'/content/{uuid}/published').json()
    assert current['payload']['document']['comments_premoderate'] == published


def test_publisher_updates_published_index(vivi, tms):
    article = '/wirtschaft/2010-01/arbeitslosenzahl-weise-bundesagentur'
    uuid = vivi.get_uuid(article)
    previous = tms(f'/content/{uuid}').json()
    # We change the value and then check that the change was propagated.
    expected = not previous['payload']['document']['comments_premoderate']

    vivi.set_property(article, 'document', 'comments_premoderate', expected)
    vivi.publish(article)

    # vivi runs the publisher asynchronously from the API call.
    timeout = 60
    for _ in range(timeout):
        sleep(1)
        current = tms(f'/content/{uuid}/published').json()
        if current and current['payload']['document']['comments_premoderate'] == expected:
            break
    else:
        pytest.fail(
            'Expected premoderate=%s, got %s after %s seconds'
            % (expected, current['payload']['document']['comments_premoderate'], timeout)
        )


def test_retract_updates_published_index(vivi, tms):
    # contentobject created manually
    content = '/wirtschaft/2010-01/nightwatch-publish-tms'
    vivi.publish(content)
    uuid = vivi.get_uuid(content)

    # vivi runs the publisher asynchronously from the API call.
    timeout = 60
    for _ in range(timeout):
        sleep(1)
        current = tms(f'/content/{uuid}/published')
        if current.status_code == 200:
            break
    else:
        pytest.fail('Expected article %s to be published after %s seconds' % (content, timeout))

    vivi.retract(content)
    timeout = 120
    for _ in range(timeout):
        sleep(1)
        current = tms(f'/content/{uuid}/published')
        if current.status_code == 404:
            break
    else:
        pytest.fail('Expected article %s to be retracted after %s seconds' % (content, timeout))
