import grokcore.component as grok

import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.references.references
import zeit.cms.related.related
import zeit.content.audio.interfaces


@grok.adapter(zeit.cms.interfaces.ICMSContent)
@grok.implementer(zeit.content.audio.interfaces.IAudioReferences)
class NoAudioReferences:
    def __init__(self, context):
        self.context = context

    @property
    def items(self):
        return ()

    def add(self, audio):
        raise NotImplementedError(f'Add audio reference not implemented for {type(self.context)}')

    def get_by_type(self, audio_type):
        return []


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.content.audio.interfaces.IAudioReferences)
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
