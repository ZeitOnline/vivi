import json
import logging
import zeit.brightcove.update2


log = logging.getLogger(__name__)


class Notification(object):
    """This view is a receiver for notification events. We register it as a
    "subscription" in the Brightcove API, and _they_ will call it each time a
    video is added/changed/deleted.

    See <https://support.brightcove.com/cms-api-notifications> for details.
    """

    def __call__(self):
        body = self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH']))
        data = json.loads(body)
        if data.get('event') != 'video-change' or not data.get('video'):
            return
        zeit.brightcove.update2.import_video_async(data.get('video'))
