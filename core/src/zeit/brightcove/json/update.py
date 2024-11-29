import json
import logging

import opentelemetry.trace

import zeit.brightcove.update
import zeit.cms.config


log = logging.getLogger(__name__)


class Notification:
    """This view is a receiver for notification events. We register it as a
    "subscription" in the Brightcove API, and _they_ will call it each time a
    video is added/changed/deleted.

    >>> api = zope.component.getUtility(zeit.brightcove.interfaces.ICMSAPI)
    >>> api._request('GET /subscriptions')
    []
    >>> api._request('POST /subscriptions', body={
        'endpoint': 'https://vivi.zeit.de/@@update_video',
        'events': ['video-change']
    })

    See <https://support.brightcove.com/cms-api-notifications> for details.
    """

    def __call__(self):
        body = self.request.bodyStream.read(int(self.request['CONTENT_LENGTH']))
        current_span = opentelemetry.trace.get_current_span()
        current_span.set_attributes({'http.body': body})

        data = json.loads(body)
        if data.get('event') != 'video-change' or not data.get('video'):
            return

        own_apikey = zeit.cms.config.required('zeit.brightcove', 'client-email')
        origin = data.get('updated_by', {})
        if origin.get('type') == 'api_key' and origin.get('email') == own_apikey:
            # Nothing left to do if we ourselves originated this change
            # (see zeit.brighcove.update.export_video).
            return

        zeit.brightcove.update.import_video_async.delay(
            data.get('video'),
            _principal_id_=zeit.cms.config.required('zeit.brightcove', 'index-principal'),
        )
