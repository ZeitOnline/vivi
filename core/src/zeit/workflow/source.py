# vim: set fileencoding=utf8 encoding=utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zc.sourcefactory.basic

import zeit.cms.content.interfaces


class _NotNeeded(object):

    def __repr__(self):
        return 'NotNeeded'

NotNeeded = _NotNeeded()


@zope.component.adapter(_NotNeeded)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVToken)
def fromNotNeeded(value):
    return 'notneeded'


class TriState(zc.sourcefactory.basic.BasicSourceFactory):
    """Source providing yes/no/notneeded."""

    _values = {
        True: u'ja',
        False: u'nein',
        NotNeeded: u'nicht nötig'}

    def getTitle(self, value):
        return self._values[value]

    def getValues(self):
        return self._values.keys()
