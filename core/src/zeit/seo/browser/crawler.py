import json

import zope.copypastemove.interfaces

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.seo.interfaces import ISEO
import zeit.cms.browser.view
import zeit.content.link.redirect


class Lightbox(zeit.cms.browser.view.Base):
    @property
    def error_messages(self):
        errors = []
        if ISEO(self.context).crawler_enabled:
            errors.append(_('Crawler already enabled'))
        return errors

    @property
    def published(self):
        return IPublishInfo(self.context).published


class EnableCrawler(zeit.cms.browser.view.Base):
    SUFFIX = '-gxe'

    def __call__(self):
        container = self.context.__parent__
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(container)
        target = f'{self.context.__name__}{self.SUFFIX}'
        renamer.renameItem(self.context.__name__, target)
        context = container[target]
        ISEO(context).crawler_enabled = True
        return self.url(context)


class CreateRedirect(zeit.cms.browser.view.Base):
    def __call__(self):
        link = zeit.content.link.redirect.create(
            self.context, self.context.uniqueId.rsplit(EnableCrawler.SUFFIX, 1)[0]
        )
        result = zeit.cms.workflow.interfaces.IPublish(link).publish()
        return json.dumps(result.id)
