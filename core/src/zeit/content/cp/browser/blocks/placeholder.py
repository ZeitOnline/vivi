import zeit.cms.interfaces
import zeit.edit.browser.view
import zope.component
import zope.event
import zope.lifecycleevent


class DropContent(zeit.edit.browser.view.Action):
    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        switcher = zope.component.getMultiAdapter(
            (self.context.__parent__, self.context, self.request), name='type-switcher'
        )
        teaserlist = switcher('teaser')
        teaserlist.insert(0, zeit.cms.interfaces.ICMSContent(self.uniqueId))
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self.context))
        self.signal('before-reload', 'deleted', self.context.__name__)
        self.signal('after-reload', 'added', teaserlist.__name__)
        self.signal(None, 'reload', self.context.__name__, self.url(teaserlist, '@@contents'))


class DropModule(zeit.edit.browser.view.Action):
    block_type = zeit.edit.browser.view.Form('block_type')

    def update(self):
        switcher = zope.component.getMultiAdapter(
            (self.context.__parent__, self.context, self.request), name='type-switcher'
        )
        new = switcher(self.block_type)
        self.signal('before-reload', 'deleted', self.context.__name__)
        self.signal('after-reload', 'added', new.__name__)
        self.signal(None, 'reload', self.context.__name__, self.url(new, '@@contents'))
