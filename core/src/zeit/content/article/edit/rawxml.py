from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import lxml.objectify
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


class RawXML(zeit.content.article.edit.block.Block):

    grok.implements(zeit.content.article.edit.interfaces.IRawXML)
    type = 'raw'


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = RawXML
    title = _('Raw XML block')

    def get_xml(self):
        E = lxml.objectify.E
        raw = getattr(E, self.element_type)()
        raw.set('alldevices', 'true')
        raw.append(E.div('\n\n', **{'class': 'article__item x-spacing'}))
        return raw
