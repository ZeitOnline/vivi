from zeit.cms.workflow.interfaces import IPublish
from zope.cachedescriptors.property import Lazy as cachedproperty
import argparse
import datetime
import logging
import requests
import zeit.cms.cli
import zeit.cms.interfaces
import zeit.content.text.text
import zeit.sourcepoint.interfaces
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.sourcepoint.interfaces.IJavaScript)
class JavaScript:

    FILENAME = 'msg_{now}.js'

    def __init__(self, folder_id, url, api_token):
        self.folder_id = folder_id
        self.url = url
        self.api_token = api_token

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
            return requests.get(
                self.url,
                headers={'Authorization': 'Token %s' % self.api_token}).text
        except Exception:
            log.warning('Error downloading %s, ignored', self.
                        url, exc_info=True)
            return None

    def _store(self, content):
        obj = zeit.content.text.text.Text()
        filename = self.FILENAME.format(
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


@zope.interface.implementer(zeit.sourcepoint.interfaces.IJavaScript)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.sourcepoint')
    return JavaScript(
        config['javascript-folder'], config['url'], config['api-token'])


@zeit.cms.cli.runner()
def update(principal=zeit.cms.cli.from_config(
        'zeit.sourcepoint', 'update-principal')):
    log.info('Checking Sourcepoint JS')
    store = zope.component.getUtility(zeit.sourcepoint.interfaces.IJavaScript)
    store.update()


@zeit.cms.cli.runner()
def sweep():
    log.info('Sweep start')
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', type=int, default=10)
    options = parser.parse_args()
    store = zope.component.getUtility(zeit.sourcepoint.interfaces.IJavaScript)
    store.sweep(keep=options.keep)
    log.info('Sweep end')
