# Copyright (c) 2006-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Standard macros for Rohbau"""

import zope.component
import zope.location.interfaces

import zope.app.basicskin.standardmacros

import z3c.flashmessage.interfaces

import zeit.cms.browser.interfaces


class StandardMacros(zope.app.basicskin.standardmacros.StandardMacros):

    macro_pages = ('main_template',)

    def messages(self):
        receiver = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageReceiver)
        return list(receiver.receive())

    @property
    def context_title(self):
        title = ''
        list_repr = zope.component.queryMultiAdapter(
            (self.context, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)
        if list_repr is not None:
            title = list_repr.title
        if not title:
            title = self.context.__name__
        if (not title
            and zope.location.interfaces.ISite.providedBy(self.context)):
                title = '/'
        if not title:
            title = str(self.context)
        return title
