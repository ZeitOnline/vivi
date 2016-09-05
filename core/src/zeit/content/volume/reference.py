import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.content.article.edit.interfaces
import zeit.content.volume.interfaces


@grok.adapter(zeit.content.volume.interfaces.IVolume, name='related')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLRelatedReference(context):
    node = lxml.objectify.E.volume(href=context.uniqueId)
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(node)
    return node


class RelatedReference(zeit.cms.content.reference.Reference):

    grok.adapts(
        zeit.content.article.edit.interfaces.IVolume,
        gocept.lxml.interfaces.IObjectified)
    grok.provides(zeit.cms.content.interfaces.IReference)
    grok.implements(zeit.content.volume.interfaces.IVolumeReference)
    grok.name('related')

    teaserText = zeit.cms.content.property.ObjectPathProperty('.teaserText')
