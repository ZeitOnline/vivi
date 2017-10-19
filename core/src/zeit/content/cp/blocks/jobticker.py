# -*- coding: utf-8 -*-
from zeit.content.cp.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.cp.interfaces
import zeit.content.modules.jobticker
import zeit.edit.block
import zope.interface


class JobTickerBlock(
        zeit.content.modules.jobticker.JobTicker,
        zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IJobTickerBlock)

    source = zeit.content.cp.interfaces.IJobTickerBlock['feed'].source


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'jobbox_ticker', _('Jobbox Ticker Block'))
