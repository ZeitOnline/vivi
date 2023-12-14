from bs4 import BeautifulSoup
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference
import zeit.content.audio.interfaces
import zeit.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IAudio)
class Audio(zeit.content.article.edit.block.Block):
    type = 'audio'
    # In the future we might switch this to use a Reference, so we can e.g.
    # express "this audio fully represents this article".
    references = zeit.content.article.edit.reference.SingleResource('.', 'related')


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
