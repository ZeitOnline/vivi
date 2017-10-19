from zeit.cms.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.quiz
import zeit.edit.block
import zope.interface


class QuizBlock(
        zeit.content.modules.quiz.Quiz,
        zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IQuizBlock)


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'quiz', _('Quiz block'))
