from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.cp.interfaces
import zeit.content.modules.jobticker


class JobTickerBlock(
        zeit.content.modules.jobticker.JobTicker,
        zeit.content.cp.blocks.block.Block):

    grok.implements(zeit.content.cp.interfaces.IJobTickerBlock)
    type = 'jobbox_ticker'

    source = zeit.content.cp.interfaces.IJobTickerBlock['feed'].source


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = JobTickerBlock
    title = _('Jobbox Ticker Block')
