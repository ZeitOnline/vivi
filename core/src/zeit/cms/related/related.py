import grokcore.component as grok
import lxml.objectify
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zeit.cms.relation.interfaces
import zope.component
import zope.interface


class RelatedBase(object):

    zope.interface.implements(zeit.cms.content.interfaces.IXMLRepresentation)
    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)

    def __init__(self, context):
        self.context = context
        # make ReferenceProperty work (XXX slightly kludgy)
        self.__parent__ = context
        self.xml = self.context.xml
        self.uniqueId = self.context.uniqueId


class RelatedContent(RelatedBase):
    """Adapter which stores related content in xml."""

    zope.interface.implements(zeit.cms.related.interfaces.IRelatedContent)

    related = zeit.cms.content.reference.MultiResource(
        '.head.references.reference', 'related')


@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.cms.related.interfaces.IRelatedContent)
def related_from_template(context):
    return RelatedContent(context)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def BasicReference(context, suppress_errors=False):
    reference = lxml.objectify.E.reference()
    reference.set('type', 'intern')
    reference.set('href', context.uniqueId)

    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(reference, suppress_errors)

    return reference


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
def create_related_reference_suppress_errors(context):
    return BasicReference(context, suppress_errors=True)


class RelatedReference(zeit.cms.content.reference.Reference):

    grok.name('related')


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def related_references(context):
    import zeit.content.cp.interfaces  # XXX circular dependency
    related = zeit.cms.related.interfaces.IRelatedContent(context, None)
    if related is None:
        return None
    return [x for x in related.related
            if not zeit.content.cp.interfaces.ICenterPage.providedBy(x)]


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_related_on_checkin(context, event):
    """Update the related metadata before checkin."""
    related = zeit.cms.related.interfaces.IRelatedContent(context, None)
    if related is None:
        return
    RelatedContent.related.update_metadata(related)
