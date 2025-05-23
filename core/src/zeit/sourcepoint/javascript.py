import ast
import logging

from zope.cachedescriptors.property import Lazy as cachedproperty
import pendulum
import requests
import zope.event

from zeit.cms.repository.interfaces import ObjectReloadedEvent
from zeit.cms.workflow.interfaces import PRIORITY_LOW, IPublish
import zeit.cms.config
import zeit.cms.interfaces
import zeit.content.text.text


log = logging.getLogger(__name__)


class JavaScript:
    FILENAME = '{prefix}_{now}.js'

    def __init__(self, folder_id, url, prefix, headers=None):
        self.folder_id = folder_id
        self.url = url
        self.prefix = prefix
        if headers:
            headers = ast.literal_eval(headers)
        self.headers = headers

    @classmethod
    def from_product_config(cls, name):
        config = zeit.cms.config.package('zeit.sourcepoint')
        return cls(
            config[f'{name}-javascript-folder'],
            config[f'{name}-url'],
            config[f'{name}-filename'],
            config.get(f'{name}-headers'),
        )

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

    def _download(self):
        log.info('Downloading from %s', self.url)
        try:
            return requests.get(self.url, headers=self.headers).text
        except Exception:
            log.warning('Error downloading %s, ignored', self.url, exc_info=True)
            return None

    def _store(self, content):
        obj = zeit.content.text.text.Text()
        filename = self.FILENAME.format(
            prefix=self.prefix, now=pendulum.now('UTC').strftime('%Y%m%d%H%M')
        )
        log.info('Storing new contents as %s/%s', self.folder_id, filename)
        obj.text = content
        self.folder[filename] = obj
        # XXX countdown is workaround race condition between celery/redis BUG-796
        IPublish(self.folder[filename]).publish(priority=PRIORITY_LOW, countdown=5)

    def sweep(self, keep):
        zope.event.notify(ObjectReloadedEvent(self.folder))  # XXX
        names = sorted(self.folder.keys())
        if len(names) <= keep:
            return
        delete = names[:-keep]
        for name in delete:
            IPublish(self.folder[name]).retract(background=False)
            del self.folder[name]
