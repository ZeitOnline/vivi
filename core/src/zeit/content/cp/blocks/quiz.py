from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface


class QuizBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IQuizBlock)

    quiz_id = zeit.cms.content.property.ObjectPathProperty(
        '.quiz_id', zeit.content.cp.interfaces.IQuizBlock['quiz_id'])


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'quiz', _('Quiz block'))
