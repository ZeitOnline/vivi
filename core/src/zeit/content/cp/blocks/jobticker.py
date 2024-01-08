import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.jobticker


@grok.implementer(zeit.content.cp.interfaces.IJobTickerBlock)
class JobTickerBlock(zeit.content.modules.jobticker.JobTicker, zeit.content.cp.blocks.block.Block):
    type = 'jobbox_ticker'

    source = zeit.content.cp.interfaces.IJobTickerBlock['feed'].source


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = JobTickerBlock
    title = _('Jobbox Ticker Block')
