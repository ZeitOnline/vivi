from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.quiz


@grok.implementer(zeit.content.article.edit.interfaces.IQuiz)
class Quiz(zeit.content.modules.quiz.Quiz, zeit.content.article.edit.block.Block):
    type = 'quiz'


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = Quiz
    title = _('Quiz block')
