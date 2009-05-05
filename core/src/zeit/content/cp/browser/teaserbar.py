# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.content.cp.browser.teaserblock
import zeit.content.cp.interfaces
import zeit.content.cp.layout
import zope.component


class EditProperties(zeit.content.cp.browser.teaserblock.EditProperties):

    interface = zeit.content.cp.interfaces.ITeaserBar

    form_fields = []

    @property
    def form(self):
        return ''


class ChangeLayout(zeit.content.cp.browser.teaserblock.ChangeLayout):

    interface = zeit.content.cp.interfaces.ITeaserBar


class Delete(zeit.cms.browser.view.Base):

    def __call__(self, key):
        teasers = [obj for obj in self.context.values()
                   if zeit.content.cp.interfaces.ITeaserBlock.providedBy(obj)]
        if len(teasers) > self.context.layout.blocks:
            # Delete the teaser block
            del self.context[key]
            return self.url(self.context)
        # Switch the teaser block into a placeholder
        switcher = zope.component.getMultiAdapter(
            (self.context, self.context[key], self.request),
            name='type-switcher')
        return self.url(switcher('placeholder'))


class Advertisement(object):

    classes = {0: None,
               1: 'adv-mr',
               2: 'adv-dmr'}

    def ad_class(self):
        blocks = (zeit.content.cp.layout.MAX_TEASER_BAR_BLOCKS
            - self.context.layout.blocks)
        return self.classes[blocks]
