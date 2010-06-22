# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import z3c.flashmessage.interfaces
import zeit.cms.content.property
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.interface


class Teaser(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(
        zeit.content.cp.interfaces.ITeaser)

    original_content = zeit.cms.content.property.SingleResource(
        '.original_content')

    default_template = u"""\
        <teaser
          xmlns:py="http://codespeak.net/lxml/objectify/pytype">
        </teaser>
    """

teaserFactory = zeit.cms.content.adapter.xmlContentFactory(Teaser)

resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'teaser')
resourceFactory = zope.component.adapter(
    zeit.content.cp.interfaces.ITeaser)(resourceFactory)


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.content.cp.interfaces.ITeaser)
def metadata_to_teaser(content):
    teaser = Teaser()
    for name in zeit.cms.content.interfaces.ICommonMetadata:
        field = zeit.cms.content.interfaces.ICommonMetadata[name]
        if zope.schema.interfaces.IField.providedBy(field):
            field = field.bind(teaser)
            value = getattr(content, name)
            try:
                field.validate(value)
            except zope.schema.interfaces.ValidationError:
                pass
            else:
                setattr(teaser, name, value)
    teaser.original_content = content
    return teaser


class TeaserLinkUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Set the link to the original article."""

    zope.component.adapts(zeit.content.cp.interfaces.ITeaser)

    def update(self, entry):
        # We don't override `update_with_context` since we don't want to adapt
        # to `ITeaser` which would create new teaser objects from articles.
        entry.set('{http://namespaces.zeit.de/CMS/link}href',
                  self.context.original_content.uniqueId)


@zope.component.adapter(zeit.content.cp.interfaces.ITeaser)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
def images_for_teaser(context):
    return zeit.content.image.interfaces.IImages(
        context.original_content, None)


@zope.component.adapter(zeit.content.cp.interfaces.ITeaser)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def teaser_references(context):
    return [context.original_content]


@zope.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata,
    zope.lifecycleevent.IObjectModifiedEvent)
def warn_about_free_teasers(context, event):
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relating_objects = relations.get_relations(context)
    for obj in relating_objects:
        if zeit.content.cp.interfaces.ITeaser.providedBy(obj):
            source = zope.component.getUtility(
                z3c.flashmessage.interfaces.IMessageSource, name='session')
            source.send(_('"${name}" is referenced by free teaser "${teaser}"',
                          mapping=dict(name=context.__name__,
                                       teaser=obj.__name__)),
                        'error')
            break
