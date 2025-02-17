from io import StringIO

import lxml.etree
import opentelemetry.trace
import requests
import zope.interface

from zeit.cms.interfaces import SHORT_TERM_CACHE
from zeit.tickaroo.interfaces import ILiveblogTimeline
import zeit.cms.config


def get_tag_text(html, tag):
    try:
        parser = lxml.etree.HTMLParser()
        tree = lxml.etree.parse(StringIO(html), parser)
        if tag is None:
            elem = tree.getroot()
        else:
            elements = tree.xpath(f'//{tag}')
            elem = elements[0]
        # Consider all text including text of child elements
        return ''.join(elem.itertext()).strip()
    except IndexError:
        opentelemetry.trace.get_current_span().add_event(
            'exception',
            {
                'exception.severity': 'warning',
                'exception.message': f'Tickaroo Liveblog: Tag {tag} not found in HTML.',
            },
        )
        return ''
    except Exception as err:
        opentelemetry.trace.get_current_span().record_exception(err)
        return ''


def get_teaser_title(html, text_length=120):
    # check post title, due to tickaroos wysiwyg editor the title can be
    # a <div><strong>...</strong></div>, <h1>...</h1> or <h2>...</h2>
    if html.startswith('<div><strong>'):
        return get_tag_text(html, 'strong')
    elif html.startswith('<h2>'):
        return get_tag_text(html, 'h2')
    elif html.startswith('<h1>'):
        return get_tag_text(html, 'h1')
    else:
        text = get_tag_text(html, None)
        if len(text) <= text_length:
            return text
        # cut text after full word and add ellipsis
        text = text[: text.rfind(' ', 0, text_length)]
        nbsp = ' '
        return text + nbsp + '…'


def get_teaser_title_from_event(event):
    for element in event['contents']:
        if 'text' in element:
            title = get_teaser_title(element['text'])
            if title:
                return title
    return None


def get_events(json):
    events = {event['local_id']: event for event in json['events']}
    # loop over event_references, because they are sorted by date
    # each event_reference points to the original event
    for event_reference in json['game'].get('events', []):
        event = events[event_reference['local_id']]
        title = get_teaser_title_from_event(event)
        if title:
            yield {
                'id': event['local_id'],
                'title': title,
            }


@zope.interface.implementer(ILiveblogTimeline)
class Tickaroo:
    def __init__(self, api_url, client_id, client_secret, timeout, default_event_limit):
        self.api_url = api_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.default_event_limit = default_event_limit

    def request_api(self, url, **params):
        params.update(
            {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
        )
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response

    @SHORT_TERM_CACHE.cache_on_arguments()
    def get_events(self, liveblog_id, **kw):
        kw.setdefault('limit', self.default_event_limit)
        try:
            response = self.request_api(url=self.api_url, id=liveblog_id, **kw)
            if response is None:
                return ()
            return tuple(get_events(response.json()))
        except Exception as exc:
            opentelemetry.trace.get_current_span().record_exception(exc)
        return ()


@zope.interface.implementer(ILiveblogTimeline)
def timeline():
    config = zeit.cms.config.package('zeit.tickaroo')
    tickaroo = Tickaroo(
        config['api-url'],
        config['client-id'],
        config['client-secret'],
        config.get('timeout', 1),
        config.get('default-event-limit', 50),
    )
    return tickaroo


@zope.interface.implementer(ILiveblogTimeline)
def MockTimeline():
    from unittest import mock  # testing dependency

    timeline = mock.Mock()
    zope.interface.alsoProvides(timeline, ILiveblogTimeline)
    timeline.get_events.return_value = ()
    return timeline
