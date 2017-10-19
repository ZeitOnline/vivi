from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.jobticker
import zeit.edit.block


class JobTicker(
        zeit.content.modules.jobticker.JobTicker,
        zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grok.implements(zeit.content.article.edit.interfaces.IJobTicker)
    type = 'jobboxticker'

    source = zeit.content.article.edit.interfaces.IJobTicker['feed'].source


class JobboxTickerBlockFactory(zeit.content.article.edit.block.BlockFactory):

    produces = JobTicker
    title = _('Jobbox ticker block')
