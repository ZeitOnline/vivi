# -*- coding: utf-8 -*-
from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface
import zeit.content.cp.interfaces


class JobboxBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IJobboxBlock,
                              zope.container.interfaces.IContained)

    @property
    def jobbox(self):
        source_id = self.xml.get('jobbox_id')
        res = zeit.content.cp.interfaces.JOBBOX_SOURCE.factory.find(
            self, source_id)
        return res

    @jobbox.setter
    def jobbox(self, value):
        self.xml.set('jobbox_id', value.id)

    @property
    def jobbox_title(self):
        jobbox = self.jobbox
        if jobbox:
            return jobbox.title

    # zope complains if there is no setter
    @jobbox_title.setter
    def jobbox_title(self, value):
        pass

zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'jobbox', _('Jobbox Block'))
