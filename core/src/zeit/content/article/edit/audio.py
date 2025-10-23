from bs4 import BeautifulSoup
import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference
import zeit.content.audio.interfaces
import zeit.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IAudio)
class Audio(zeit.content.article.edit.reference.Reference):
    type = 'audio'
    # In the future we might switch this to use a Reference, so we can e.g.
    # express "this audio fully represents this article".
    _references = zeit.content.article.edit.reference.SingleResource('.', 'related')

    @property
    def references(self):
        return self._references

    @references.setter
    def references(self, value):
        self._references = value
        self.is_empty = value is None


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = Audio
    title = _('Audio')


@grok.adapter(
    zeit.content.article.edit.interfaces.IArticleArea, zeit.content.audio.interfaces.IAudio, int
)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_content(body, context, position):
    block = Factory(body)(position)
    block.references = context
    return block


def apply_notes(body, episode_info):
    notes = BeautifulSoup(episode_info.notes, 'html.parser')
    mapping = {
        'p': 'p',
        'ul': 'ul',
        'ol': 'ol',
        'h1': 'intertitle',
        'h2': 'intertitle',
        'h3': 'intertitle',
    }
    for item in notes.contents:
        tag_name = mapping.get(item.name, 'p')
        body.create_item(tag_name).text = str(item)
