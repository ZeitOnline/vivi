# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import z3c.flashmessage.interfaces
import zeit.content.cp.interfaces
import zope.component

def validate(context):
    validator = zeit.content.cp.interfaces.IValidator(context)
    css_class = ''
    if validator.status:
        css_class = 'validation-%s' % validator.status
    source = zope.component.getUtility(
        z3c.flashmessage.interfaces.IMessageSource, name='session')
    for m in validator.messages:
        source.send(m, 'message')
    return css_class
