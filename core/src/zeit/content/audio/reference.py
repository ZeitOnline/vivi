import zope.interface

import zeit.cms.content.reference
import zeit.cms.related.related
import zeit.content.audio.interfaces


@zope.interface.implementer(zeit.content.audio.interfaces.IAudioReferences)
class AudioReferences(zeit.cms.related.related.RelatedBase):
    items = zeit.cms.content.reference.MultiResource('.head.audio', 'related')

    def add(self, audio):
        self.items += (audio,)

    def get_by_type(self, audio_type):
        return [i for i in self.items if audio_type == i.audio_type]
