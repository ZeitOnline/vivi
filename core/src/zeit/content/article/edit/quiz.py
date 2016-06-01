from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import IQuiz
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class Quiz(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.implements(IQuiz)
    type = 'quiz'

    quiz_id = ObjectPathAttributeProperty(
        '.', 'quiz_id', IQuiz['quiz_id'])

    adreload_enabled = ObjectPathAttributeProperty(
        '.', 'adreload_enabled', IQuiz['adreload_enabled'])

    def __init__(self, *args, **kw):
        super(Quiz, self).__init__(*args, **kw)
        if self.adreload_enabled is None:
            self.adreload_enabled = IQuiz['adreload_enabled'].default


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Quiz
    title = _('Quiz block')
