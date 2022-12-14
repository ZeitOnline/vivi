from zeit.cms.workflow.interfaces import IPublish
from zope.cachedescriptors.property import Lazy as cachedproperty

import datetime
import logging
import requests

import zeit.cms.interfaces
import zeit.content.text.text


log = logging.getLogger(__name__)


class JavaScript:

    FILENAME = '{prefix}_{now}.js'

    def __init__(self, folder_id, url, prefix):
        self.folder_id = folder_id
        self.url = url
        self.prefix = prefix

    @cachedproperty
    def folder(self):
        return zeit.cms.interfaces.ICMSContent(self.folder_id)

    @property
    def latest_version(self):
        names = sorted(self.folder.keys(), reverse=True)
        if not names:
            return None
        return self.folder[names[0]]

    def update(self):
        current = self.latest_version
        if current is not None:
            current = current.text
        new = self._download()
        if new and new != current:
            self._store(new)

    def _request_text(self):
        return requests.get(self.url).text

    def _download(self):
        log.info('Downloading from %s', self.url)
        try:
            return self._request_text()
        except Exception:
            log.warning('Error downloading %s, ignored', self.
                        url, exc_info=True)
            return None

    def _store(self, content):
        obj = zeit.content.text.text.Text()
        filename = self.FILENAME.format(
            prefix=self.prefix,
            now=datetime.datetime.now().strftime('%Y%m%d%H%M'))
        log.info('Storing new contents as %s/%s', self.folder_id, filename)
        obj.text = content
        self.folder[filename] = obj
        IPublish(self.folder[filename]).publish(background=False)

    def sweep(self, keep):
        names = sorted(self.folder.keys())
        if len(names) <= keep:
            return
        delete = names[:-keep]
        for name in delete:
            IPublish(self.folder[name]).retract(background=False)
            del self.folder[name]


class Sourcepoint(JavaScript):

    def __init__(self, folder_id, url, api_token, prefix):
        self.folder_id = folder_id
        self.url = url
        self.api_token = api_token
        self.prefix = prefix

    def _request_text(self):
        return requests.get(
                self.url,
                headers={'Authorization': 'Token %s' % self.api_token}).text
