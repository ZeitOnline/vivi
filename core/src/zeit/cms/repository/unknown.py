# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO
import datetime

import zope.component
import zope.interface

import zope.app.container.contained

import zeit.cms.connector
import zeit.cms.interfaces
import zeit.cms.content.interfaces

import zeit.cms.repository.interfaces


class UnknownResource(zope.app.container.contained.Contained):
    """Represent an unknown resource"""

    zope.interface.implements(zeit.cms.repository.interfaces.IUnknownResource,
                              zeit.cms.content.interfaces.ITextContent)

    def __init__(self, data, type_info=None):
        if not isinstance(data, unicode):
            raise TypeError('data must be unicode.')
        self.data = data
        self.type = type_info

        # provide suitable defaults for year and volume and online
        now = datetime.datetime.now()
        self.year = now.year
        self.volume = int(now.strftime('%W'))
        self.ressort = 'online'

        # we don't have a unique id initially:
        self.uniqueId = None


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def unknownResourceFactory(context):
    res = UnknownResource(unicode(context.data.read(), 'latin1'), context.type)
    return res


@zope.interface.implementer(zeit.cms.interfaces.IResource)
@zope.component.adapter(zeit.cms.repository.interfaces.IUnknownResource)
def resourceFactory(context):
    return zeit.cms.connector.Resource(
        context.uniqueId, context.__name__, 'unknown',
        StringIO.StringIO(context.data.encode('latin1')),
        properties=zeit.cms.interfaces.IWebDAVProperties(context))
