# -*- coding: utf-8 -*-
from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface
import zeit.content.cp.interfaces


class JobboxTickerBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IJobboxTickerBlock,
                              zope.container.interfaces.IContained)

    @property
    def jobbox_ticker(self):
        source_id = self.xml.get('jobbox_ticker_id')
        res = zeit.content.cp.interfaces.JOBBOX_TICKER_SOURCE.factory.find(
            self, source_id)
        return res

    @jobbox_ticker.setter
    def jobbox_ticker(self, value):
        self.xml.set('jobbox_ticker_id', value.id)

    @property
    def jobbox_ticker_title(self):
        jobbox_ticker = self.jobbox_ticker
        if jobbox_ticker:
            return jobbox_ticker.title

    # zope complains if there is no setter
    @jobbox_ticker_title.setter
    def jobbox_ticker_title(self, value):
        pass

zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'jobbox_ticker', _('Jobbox Ticker Block'))
