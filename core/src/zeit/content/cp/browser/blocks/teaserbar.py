# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks.teaser
import zeit.content.cp.interfaces
import zope.component


class EditProperties(zeit.content.cp.browser.blocks.teaser.EditProperties):

    interface = zeit.content.cp.interfaces.ITeaserBar
    layout_prefix  = 'teaserbar'

    form_fields = []

    @property
    def form(self):
        return ''


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):

    interface = zeit.content.cp.interfaces.ITeaserBar


class Delete(zeit.content.cp.browser.view.Action):

    key = zeit.content.cp.browser.view.Form('key')

    def update(self):
        teasers = [
            obj for obj in self.context.values()
            if not zeit.content.cp.interfaces.IPlaceHolder.providedBy(obj)]
        if len(teasers) > self.context.layout.blocks:
            # Delete the teaser block
            del self.context[self.key]
        else:
            # Switch the teaser block into a placeholder
            switcher = zope.component.getMultiAdapter(
                (self.context, self.context[self.key], self.request),
                name='type-switcher')
            new = switcher('placeholder')
            self.signal('after-reload', 'added', new.__name__)
        self.signal('before-reload', 'deleted', self.key)
        self.signal(
            None, 'reload', self.context.__name__, self.url(self.context,
                                                            '@@contents'))
