import json

import zope.copypastemove.interfaces

import zeit.cms.browser.view
import zeit.content.link.redirect


class EnableCrawler(zeit.cms.browser.view.Base):
    SUFFIX = '-gxe'

    def __call__(self):
        container = self.context.__parent__
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(container)
        target = f'{self.context.__name__}{self.SUFFIX}'
        renamer.renameItem(self.context.__name__, target)
        return self.url(container[target])


class CreateRedirect(zeit.cms.browser.view.Base):
    def __call__(self):
        link = zeit.content.link.redirect.create(
            self.context, self.context.uniqueId.rsplit(EnableCrawler.SUFFIX, 1)[0]
        )
        result = zeit.cms.workflow.interfaces.IPublish(link).publish()
        return json.dumps(result.id)
