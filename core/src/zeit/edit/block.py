import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import urllib.parse
import zeit.cms.content.xmlsupport
import zeit.edit.interfaces
import zope.component
import zope.interface
import zope.traversing.api


@zope.component.adapter(zeit.edit.interfaces.IContainer, gocept.lxml.interfaces.IObjectified)
@zope.interface.implementer(zeit.edit.interfaces.IElement)
class Element(zope.container.contained.Contained, zeit.cms.content.xmlsupport.Persistent):
    """Base class for blocks."""

    def __init__(self, context, xml):
        self.xml = xml
        # Set parent last so we don't trigger a write.
        self.__parent__ = context

    def __eq__(self, other):
        if not zeit.edit.interfaces.IElement.providedBy(other):
            return False
        if self.__name__ and other.__name__:
            return self.__name__ == other.__name__

        self_xml = zope.security.proxy.getObject(self.xml)
        other_xml = zope.security.proxy.getObject(other.xml)
        return xml_tree_equal(self_xml, other_xml)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.uniqueId)

    @property
    def __name__(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}__name__')

    @__name__.setter
    def __name__(self, name):
        if name != self.__name__:
            self._p_changed = True
            self.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', name)

    @property
    def type(self):
        return self.xml.get('{http://namespaces.zeit.de/CMS/cp}type')

    @property
    def uniqueId(self):
        parent = getattr(self.__parent__, 'uniqueId', '')
        if not parent.startswith(zeit.edit.interfaces.BLOCK_NAMESPACE):
            return '%s%s#%s' % (zeit.edit.interfaces.BLOCK_NAMESPACE, parent, self.__name__)
        else:
            name = self.__name__
            if name is None:
                # XXX Since Container does not generally support index(),
                # this won't generally work. It's only implemented for
                # z.c.article.edit.Body at the moment.
                name = self.__parent__.index(self)
            return '%s/%s' % (parent, name)

    def __repr__(self):
        try:
            uniqueId = self.uniqueId.encode('ascii', 'replace')
        except Exception:
            uniqueId = '(unknown)'
        return '<%s.%s %s>' % (self.__class__.__module__, self.__class__.__name__, uniqueId)


def xml_tree_equal(a, b):
    for prop in ['tag', 'attrib', 'text', 'tail']:
        a_val = getattr(a, prop)
        b_val = getattr(b, prop)
        if a_val != b_val:
            return False

    a_children = a.getchildren()
    b_children = b.getchildren()
    if len(a_children) != len(b_children):
        return False

    for a_child, b_child in zip(a_children, b_children):
        if not xml_tree_equal(a_child, b_child):
            return False

    return True


@grok.adapter(str, name='http://block.vivi.zeit.de/')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def resolve_block_id(context):
    parts = urllib.parse.urlparse(context)
    assert parts.path.startswith('/')
    path = parts.path[1:]
    content = zeit.cms.cmscontent.resolve_wc_or_repository(path)
    return zope.traversing.api.traverse(content, parts.fragment)


class SimpleElement(Element):
    grok.baseclass()


@grok.adapter(zeit.edit.interfaces.IElement)
@grok.implementer(zeit.edit.interfaces.IArea)
def area_for_element(context):
    return zeit.edit.interfaces.IArea(context.__parent__, None)


@grok.implementer(zeit.edit.interfaces.IElementFactory)
class ElementFactory:
    """Base class for element factories."""

    grok.baseclass()

    produces = NotImplemented
    element_type = NotImplemented  # Deduced from produces by grokker

    def __init__(self, context):
        self.context = context

    def get_xml(self):
        raise NotImplementedError('Implemented in subclasses.')

    def __call__(self, position=None):
        container = self.get_xml()
        content = zope.component.getMultiAdapter(
            (self.context, container), zeit.edit.interfaces.IElement, name=self.element_type
        )

        if position is not None:
            self.context.insert(position, content)
        else:
            self.context.add(content)
        return content

    @property
    def provided_interface(self):
        """Retrieves the interface from the element created via the factory.

        Caution: Only works with elements that are registered using grok.

        """
        element = zope.component.getSiteManager().adapters.lookup(
            list(map(zope.interface.providedBy, (self.context, self.get_xml()))),
            zeit.edit.interfaces.IElement,
            name=self.element_type,
        )
        return getattr(element, 'grokcore.component.directive.provides', None)


class TypeOnAttributeElementFactory(ElementFactory):
    grok.baseclass()
    tag_name = 'container'

    def get_xml(self):
        container = getattr(lxml.objectify.E, self.tag_name)()
        container.set('{http://namespaces.zeit.de/CMS/cp}type', self.element_type)
        container.set('module', self.module)  # XXX Why? Who needs this?
        return container

    @property
    def module(self):
        return self.element_type


@zope.interface.implementer(zeit.edit.interfaces.IUnknownBlock)
class UnknownBlock(SimpleElement):
    area = zeit.edit.interfaces.IArea
    type = '__unknown__'
