from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import lxml.objectify
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces


class XMLBlock(zeit.content.cp.blocks.block.Block):

    grok.implements(zeit.content.cp.interfaces.IXMLBlock)
    type = 'xml'


class XMLBlockFactory(zeit.content.cp.blocks.block.BlockFactory):

    produces = XMLBlock
    title = _('Raw XML block')

    def get_xml(self):
        container = super(XMLBlockFactory, self).get_xml()
        raw = lxml.objectify.E.raw(u'\n\n\n')
        lxml.objectify.deannotate(raw)
        container.append(raw)
        return container
