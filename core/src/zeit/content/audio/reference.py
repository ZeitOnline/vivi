import zope.interface
import zeit.cms.related.related
import zeit.cms.content.reference
import zeit.content.audio.interfaces


@zope.interface.implementer(zeit.content.audio.interfaces.IAudioReferences)
class AudioReferences(zeit.cms.related.related.RelatedBase):
    items = zeit.cms.content.reference.MultiResource('.head.audio', 'related')
