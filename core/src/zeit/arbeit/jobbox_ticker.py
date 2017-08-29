from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.arbeit.interfaces
import zeit.cms.content.dav
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zope.interface


class JobboxTicker(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grok.implements(zeit.arbeit.interfaces.IJobboxTicker)
    type = 'jobboxticker'

    _jobbox = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty(
            '.', 'id'), zeit.arbeit.interfaces.IJobboxTicker['jobbox'])

    @property
    def jobbox(self):
        # Since the values come in via xml config file, we cannot declare the
        # default on the field without major hassle.
        if self._jobbox is None:
            source = zeit.arbeit.interfaces.IJobboxTicker['jobbox'].source(self)
            return source.find('default')
        return self._jobbox

    @jobbox.setter
    def jobbox(self, value):
        self._jobbox = value


class JobboxTickerBlockFactory(zeit.content.article.edit.block.BlockFactory):

    produces = JobboxTicker
    title = _('Jobbox ticker block')
