# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.i18nmessageid
import zope.interface
import zope.schema

import zope.app.container.interfaces

import zc.form.field


_ = zope.i18nmessageid.MessageFactory('zeit.cms')


DOCUMENT_SCHEMA_NS = u"http://namespaces.zeit.de/CMS/document"
ID_NAMESPACE = u'http://xml.zeit.de/'
TEASER_NAMESPACE = u'http://xml.zeit.de/CMS/Teaser'

# Backward compatibility imports
from zeit.connector.interfaces import (
    DeleteProperty, LockingError, IConnector, IResource,
    IWebDAVReadProperties, IWebDAVWriteProperties, IWebDAVProperties)


class ICMSContentType(zope.interface.interfaces.IInterface):
    """Interface for content types."""


class ICMSContent(zope.interface.Interface):
    """Interface for all CMS content being loaded from the repository.

    """

    uniqueId = zope.schema.TextLine(
        title=_("Unique Id"),
        readonly=True)

    __name__ = zope.schema.TextLine(
        title=_("File name"))
