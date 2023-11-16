# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IPuzzleForm)
class PuzzleForm(zeit.content.article.edit.block.Block):
    type = 'puzzleform'

    puzzle_type = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'id'),
        zeit.content.article.edit.interfaces.IPuzzleForm['puzzle_type'],
    )

    year = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'year', zeit.content.article.edit.interfaces.IPuzzleForm['year']
    )


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = PuzzleForm
    title = _('Puzzle Form Block')
