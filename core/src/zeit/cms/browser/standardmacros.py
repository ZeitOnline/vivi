# Copyright (c) 2006-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Standard macros for Rohbau"""

import zope.component

import zope.app.basicskin.standardmacros

import z3c.flashmessage.interfaces


class StandardMacros(zope.app.basicskin.standardmacros.StandardMacros):

    macro_pages = ('main_template',)

    def messages(self):
        receiver = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageReceiver)
        return list(receiver.receive())
