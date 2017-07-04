import json
import logging
import zeit.brightcove.update2


log = logging.getLogger(__name__)


class Notification(object):

    def __call__(self):
        body = self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH']))
        data = json.loads(body)
        if data.get('event') != 'video-change' or not data.get('video'):
            return
        zeit.brightcove.update2.import_video_async(data.get('video'))
