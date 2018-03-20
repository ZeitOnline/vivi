# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


class PuzzleForm(zeit.content.article.edit.block.Block):

    grok.implements(zeit.content.article.edit.interfaces.IPuzzleForm)
    type = 'puzzleform'

    _puzzle_type_id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'puzzle_type_id')

    year = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'year', zeit.content.article.edit.interfaces.IPuzzleForm['year'])

    @property
    def puzzle_type(self):
        source = zeit.content.article.edit.interfaces.IPuzzleForm[
            'puzzle_type'].source(self)
        for value in source:
            if value.id == self._puzzle_type_id:
                return value

    @puzzle_type.setter
    def puzzle_type(self, value):
        if self._puzzle_type_id == value.id:
            return
        self._puzzle_type_id = value.id if value is not None else None


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = PuzzleForm
    title = _('Puzzle Form Block')
