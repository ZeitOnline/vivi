import grokcore.component as grok
import lxml.builder
import zope.component
import zope.interface

import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.related.interfaces


@zope.component.adapter(zeit.cms.content.interfaces.IXMLContent)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLRepresentation)
class RelatedBase(zeit.cms.content.xmlsupport.Persistent):
    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.uniqueId = self.context.uniqueId
        # Make ReferenceProperty and Persistent work (set parent last so we
        # don't trigger a write).
        self.__parent__ = context


@zope.interface.implementer(zeit.cms.related.interfaces.IRelatedContent)
class RelatedContent(RelatedBase):
    """Adapter which stores related content in xml."""

    related = zeit.cms.content.reference.MultiResource('.head.references.reference', 'related')


@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.cms.related.interfaces.IRelatedContent)
def related_from_template(context):
    return RelatedContent(context)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def BasicReference(context, suppress_errors=False):
    reference = lxml.builder.E.reference()
    reference.set('type', 'intern')
    reference.set('href', context.uniqueId)

    return reference


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def create_related_reference_suppress_errors(context):
    return BasicReference(context, suppress_errors=True)


class RelatedReference(zeit.cms.content.reference.Reference):
    grok.name('related')
