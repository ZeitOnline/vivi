import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference


@grok.implementer(zeit.content.article.edit.interfaces.IScrollyChapter)
class ScrollyChapter(zeit.content.article.edit.reference.Reference):
    type = 'scrolly_chapter'

    kicker = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'kicker', zeit.content.article.edit.interfaces.IScrollyChapter['kicker']
    )
    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title', zeit.content.article.edit.interfaces.IScrollyChapter['title']
    )
    font_style = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'font-style',
        zeit.content.article.edit.interfaces.IScrollyChapter['font_style'],
        use_default=True,
    )


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = ScrollyChapter
    title = _('Scrollytelling Chapter')
