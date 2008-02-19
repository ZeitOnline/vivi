# vim: set fileencoding=utf8 encoding=utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zc.sourcefactory.basic

import zeit.cms.content.interfaces
from zeit.cms.i18n import MessageFactory as _


class _NotNecessary(object):

    def __repr__(self):
        return 'NotNecessary'

NotNecessary = _NotNecessary()


@zope.component.adapter(_NotNecessary)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromNotNecessary(value):
    return 'notnecessary'


class TriState(zc.sourcefactory.basic.BasicSourceFactory):
    """Source providing yes/no/notnecessary."""

    _values = {
        True: _('yes'),
        False: _('no'),
        NotNecessary: _('not necessary')}

    def getTitle(self, value):
        return self._values[value]

    def getValues(self):
        return self._values.keys()
