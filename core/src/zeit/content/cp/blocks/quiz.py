from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.quiz


class QuizBlock(
        zeit.content.modules.quiz.Quiz,
        zeit.content.cp.blocks.block.Block):

    grok.implements(zeit.content.cp.interfaces.IQuizBlock)
    type = 'quiz'

    # XXX somehow we use a PathProperty here, but an AttributeProperty on
    # articles, sigh.
    quiz_id = zeit.cms.content.property.ObjectPathProperty(
        '.quiz_id', zeit.content.cp.interfaces.IQuizBlock['quiz_id'])


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = QuizBlock
    title = _('Quiz block')
