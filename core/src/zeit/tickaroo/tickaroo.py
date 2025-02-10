from io import StringIO
import logging

# import bleach
import lxml.etree
import requests

import zeit.cms.config


log = logging.getLogger(__name__)


def get_tag_text(html, tag):
    try:
        parser = lxml.etree.HTMLParser()
        tree = lxml.etree.parse(StringIO(html), parser)
        elements = tree.xpath(f'//{tag}')
        # Consider all text including text of child elements
        return ''.join(elements[0].itertext()).strip()
    except IndexError:
        log.error(f'Tickaroo Liveblog: Tag {tag} not found in HTML.')
        return ''
    except Exception as err:
        log.error(f'Tickaroo Liveblog: error extracting tag text: {err}')
        return ''


def get_teaser_title(html, text_length=120):
    # check post title, due to tickaroos wysiwyg editor the title can be
    # a <div><strong>...</strong></div> or <h2>...</h2>
    if html.startswith('<div><strong>'):
        return get_tag_text(html, 'strong')
    elif html.startswith('<h2>'):
        return get_tag_text(html, 'h2')
    elif html.startswith('<h1>'):
        return get_tag_text(html, 'h1')
    else:
        print(html)
        # text = bleach.clean(html, tags=[], strip=True)
        text = html
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


def liveblog_is_healthy(settings):
    return True


UNSET = {}


class Tickaroo:
    def settings(self, key=None, default=UNSET):
        if key is None:
            return zeit.cms.config.package('zeit.tickaroo')
        if default is UNSET:
            return zeit.cms.config.required('zeit.tickaroo', key)
        return zeit.cms.config.get('zeit.tickaroo', key, default=default)

    def config(self):
        return {'id': self.liveblog_id, 'clientId': self.settings('client-id')}

    def request_api(self, url, metrics_id, **params):
        if not liveblog_is_healthy(self.settings()):
            return None
        params.update(
            {
                'client_id': self.settings('client-id'),
                'client_secret': self.settings('client-secret'),
            }
        )
        timeout = self.settings('liveblog-timeout', 1)
        # with zeit.web.core.metrics.http(
        #    metrics_id,
        #    {
        #        'http.url': url,
        #        'http.query': str(params),
        #        'http.timeout': timeout,
        #    },
        # ) as record:
        response = requests.get(url, params=params, timeout=timeout)
        #    record(response)
        response.raise_for_status()
        return response

    def get_events(self, **kw):
        kw.setdefault('limit', self.settings('teaser-limit', 20))
        try:
            response = self.request_api(
                url=self.settings('api-url'),
                metrics_id='tickaroo.events',
                id=self.liveblog_id,
                **kw,
            )
            if response is None:
                return []
            return list(get_events(response.json()))
        except requests.exceptions.RequestException:
            log.error('Tickaroo Liveblog Show API unavailable', exc_info=True)
        except Exception:
            log.error('Tickaroo Liveblog Events Exception', exc_info=True)
        return []
