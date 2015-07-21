import copy
import grokcore.component as grok
import zeit.cms.content.property
import zeit.content.cp.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component
import zope.interface


@zope.interface.implementer(zeit.content.cp.interfaces.ICenterPage)
@zope.component.adapter(zeit.edit.interfaces.IElement)
def cms_content_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.__parent__, None)


@zope.component.adapter(zeit.edit.interfaces.IElement)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return iter([])


class VisibleMixin(object):

    visible = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'visible', zeit.content.cp.interfaces.IElement[
            'visible'])

    visible_mobile = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'visible_mobile', zeit.content.cp.interfaces.IElement[
            'visible_mobile'])

    def __init__(self, context, xml):
        super(VisibleMixin, self).__init__(context, xml)
        if 'visible' not in self.xml.attrib:
            self.visible = zeit.content.cp.interfaces.IElement[
                'visible'].default
        if 'visible_mobile' not in self.xml.attrib:
            self.visible_mobile = zeit.content.cp.interfaces.IElement[
                'visible_mobile'].default


class Block(VisibleMixin, zeit.edit.block.Element):

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle')
    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title')

    publisher = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'publisher')
    publisher_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'publisher_url')

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle')
    supertitle_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle_url')

    read_more = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more')
    read_more_url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'read_more_url')

    background_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'background_color')


@grok.adapter(zeit.content.cp.interfaces.IBlock)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    return copy.copy(context.xml)
