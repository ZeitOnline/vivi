import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.quiz


@grok.implementer(zeit.content.cp.interfaces.IQuizBlock)
class QuizBlock(zeit.content.modules.quiz.Quiz, zeit.content.cp.blocks.block.Block):
    type = 'quiz'

    # XXX somehow we use a PathProperty here, but an AttributeProperty on
    # articles, sigh.
    quiz_id = zeit.cms.content.property.ObjectPathProperty(
        '.quiz_id', zeit.content.cp.interfaces.IQuizBlock['quiz_id']
    )


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = QuizBlock
    title = _('Quiz block')
