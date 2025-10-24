import grokcore.component as grok
import zope.component
import zope.interface

import zeit.cms.content.reference
import zeit.cms.references.references
import zeit.cms.related.related
import zeit.content.audio.interfaces


@zope.component.adapter(zeit.content.article.interfaces.IArticle)
@zope.interface.implementer(zeit.content.audio.interfaces.IAudioReferences)
class AudioReferences(zeit.cms.related.related.RelatedBase):
    items = zeit.cms.content.reference.MultiResource('.head.audio', 'related')

    def add(self, audio):
        self.items += (audio,)

    def get_by_type(self, audio_type):
        return [i for i in self.items if audio_type == i.audio_type]


class ExtractAudioReferences(zeit.cms.references.references.Extract):
    interface = zeit.content.audio.interfaces.IAudioReferences
    grok.name(interface.__name__)

    def __call__(self):
        return [{'target': x, 'type': f'audio-{x.audio_type}'} for x in self.context.items]
