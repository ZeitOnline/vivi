import logging


log = logging.getLogger(__name__)


class Notification:
    """This view is a receiver for notification events. We register it as a
    webhook in the Simplecast API, and _they_ will call it each time a
    podcast or episode is added/changed/deleted.
    """

    def __call__(self):
        body = self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH']))
        log.info(body)
