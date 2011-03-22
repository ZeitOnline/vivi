# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.blocks.teaser import create_xi_include
from zeit.content.cp.i18n import MessageFactory as _
import grokcore.component
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.content.xmlsupport
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.quiz.interfaces
import zope.component
import zope.interface


class QuizBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IQuizBlock)

    referenced_quiz = zeit.cms.content.property.SingleResource(
        '.block', xml_reference_name='related', attributes=('href',))


zeit.content.cp.blocks.block.register_element_factory(
    [zeit.content.cp.interfaces.IInformatives,
     zeit.content.cp.interfaces.ITeaserBar],
    'quiz', _('Quizblock'))


@grokcore.component.adapter(zeit.content.cp.interfaces.IQuizBlock)
@grokcore.component.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    quiz = context.referenced_quiz
    if quiz is not None:
        yield quiz
