from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.quiz
import zeit.edit.block


class Quiz(
        zeit.content.modules.quiz.Quiz,
        zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.implements(zeit.content.article.edit.interfaces.IQuiz)
    type = 'quiz'


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Quiz
    title = _('Quiz block')
