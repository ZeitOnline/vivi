# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.content.xmlsupport
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.component
import zope.interface

class QuizBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IQuizBlock)

    referenced_quiz = zeit.cms.content.property.SingleResource(
        '.block', xml_reference_name='related', attributes=('href',))

QuizBlockFactory = zeit.content.cp.blocks.block.elementFactoryFactory(
    zeit.content.cp.interfaces.IRegion, 'quizblock',
    _('Quizblock'), module='quiz')
