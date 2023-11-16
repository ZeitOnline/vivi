from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.jobticker


@grok.implementer(zeit.content.article.edit.interfaces.IJobTicker)
class JobTicker(zeit.content.modules.jobticker.JobTicker, zeit.content.article.edit.block.Block):
    type = 'jobboxticker'

    source = zeit.content.article.edit.interfaces.IJobTicker['feed'].source


class JobboxTickerBlockFactory(zeit.content.article.edit.block.BlockFactory):
    produces = JobTicker
    title = _('Jobbox ticker block')
