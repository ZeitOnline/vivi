import grokcore.component as grok
import lxml.builder

import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.volume.interfaces


@grok.adapter(zeit.content.volume.interfaces.IVolume, name='related')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLRelatedReference(context):
    node = lxml.builder.E.volume(href=context.uniqueId)
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(node)
    return node


@grok.implementer(zeit.content.volume.interfaces.IVolumeReference)
class RelatedReference(zeit.cms.content.reference.Reference):
    grok.adapts(zeit.content.article.edit.interfaces.IVolume, zeit.cms.interfaces.IXMLElement)
    grok.provides(zeit.cms.content.interfaces.IReference)
    grok.name('related')

    _teaserText_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'teasertext_local', zeit.content.volume.interfaces.IVolumeReference['teaserText']
    )
    teaserText = zeit.cms.content.reference.OverridableProperty(
        zeit.content.volume.interfaces.IVolume['teaserText'], original='target'
    )
