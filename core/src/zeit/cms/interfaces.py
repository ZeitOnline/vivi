# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import re

import zope.i18nmessageid
import zope.interface
import zope.schema

import zope.app.container.interfaces

import zc.form.field

from zeit.cms.i18n import MessageFactory as _


DOCUMENT_SCHEMA_NS = u"http://namespaces.zeit.de/CMS/document"
QPS_SCHEMA_NS = u"http://namespaces.zeit.de/QPS/attributes"
ID_NAMESPACE = u'http://xml.zeit.de/'
TEASER_NAMESPACE = u'http://xml.zeit.de/CMS/Teaser'

# Backward compatibility imports
from zeit.connector.interfaces import (
    DeleteProperty, LockingError, IConnector, IResource,
    IWebDAVReadProperties, IWebDAVWriteProperties, IWebDAVProperties)


class ICMSContentType(zope.interface.interfaces.IInterface):
    """Interface for content types."""


valid_name_regex = re.compile(r'^[A-Za-z0-9\.\,\-_*()~]+$').match
def valid_name(value):
    if valid_name_regex(value):
        return True
    return False


class ICMSContent(zope.interface.Interface):
    """Interface for all CMS content being loaded from the repository.

    """

    uniqueId = zope.interface.Attribute("Unique Id")

    __name__ = zope.schema.TextLine(
        title=_("File name"),
        readonly=True,
        constraint=valid_name)
