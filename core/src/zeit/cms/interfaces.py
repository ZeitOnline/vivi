# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import re
import zope.app.container.interfaces
import zope.i18nmessageid
import zope.interface
import zope.schema
import zope.security


DOCUMENT_SCHEMA_NS = u"http://namespaces.zeit.de/CMS/document"
QPS_SCHEMA_NS = u"http://namespaces.zeit.de/QPS/attributes"
ID_NAMESPACE = u'http://xml.zeit.de/'
TEASER_NAMESPACE = u'http://xml.zeit.de/CMS/Teaser'
PRINT_NAMESPACE = u"http://namespaces.zeit.de/CMS/print"

# Backward compatibility imports
from zeit.connector.interfaces import (
    DeleteProperty, LockingError, IConnector, IResource,
    IWebDAVReadProperties, IWebDAVWriteProperties, IWebDAVProperties)


class ICMSContentType(zope.interface.interfaces.IInterface):
    """Interface for content types."""


class InvalidName(zope.schema.ValidationError):
    __doc__ = _('Name contains invalid characters')


valid_name_regex = re.compile(r'^[A-Za-z0-9\.\,\-_*()~]+$').match


def valid_name(value):
    if not valid_name_regex(value):
        raise InvalidName(value)
    return True


class ICMSContent(zope.interface.Interface):
    """Interface for all CMS content being loaded from the repository.

    """

    uniqueId = zope.interface.Attribute("Unique Id")

    __name__ = zope.schema.TextLine(
        title=_("File name"),
        readonly=True,
        constraint=valid_name)


class IEditorialContent(ICMSContent):
    """Editorial content.

    Editorial content is content which actually *is* content. That is in
    contrast to for example folders which are used for structuring.

    """


class IAsset(ICMSContent):
    """Assets are special, usually simple, content objects.

    Assets are useles themselves but are integrated into other objects.
    An example is the image.

    """


class IEditPermission(zope.security.interfaces.IPermission):
    """A permission which is always forbidden in the repository."""


class ITypeDeclaration(zope.interface.Interface):

    type_identifier = zope.schema.TextLine(
        title=u'Unique identifier for this type')

    # XXX add other attributes
