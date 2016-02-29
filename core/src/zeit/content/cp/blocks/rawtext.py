from zeit.content.cp.i18n import MessageFactory as _
import lxml.objectify
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.container.interfaces
import zope.interface


class RawTextXMLBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IXMLBlock,
        zope.container.interfaces.IContained)


class RawTextXMLBlockFactory(zeit.edit.block.TypeOnAttributeElementFactory):

    zope.component.adapts(zeit.content.cp.interfaces.IArea)
    element_type = module = 'rawtext'
    title = _('Raw Text block')

    def get_xml(self):
        container = super(RawTextXMLBlockFactory, self).get_xml()

        # NEED CDATA HANDLING HERE
        raw = lxml.objectify.E.raw(u'\n\n\n')
        lxml.objectify.deannotate(raw)
        container.append(raw)
        return container


class RawTextBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IRawTextBlock)

    raw = zeit.cms.content.reference.SingleResource('.rawtext','related')


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'rawtext', _('raw text block'))

