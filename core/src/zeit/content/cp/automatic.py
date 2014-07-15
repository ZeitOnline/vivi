import zeit.cms.content.property
import zeit.content.cp.interfaces
import zope.component
import zope.interface


class AutomaticRegion(zeit.cms.content.xmlsupport.Persistent):

    zope.component.adapts(zeit.content.cp.interfaces.IRegion)
    zope.interface.implements(zeit.content.cp.interfaces.IAutomaticRegion)

    automatic = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic',
        zeit.content.cp.interfaces.IAutomaticRegion['automatic'])

    count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', zeit.content.cp.interfaces.IAutomaticRegion['count'])

    query = zeit.cms.content.property.ObjectPathProperty(
        '.query.raw', zeit.content.cp.interfaces.IAutomaticRegion['query'])

    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.__parent__ = self.context
