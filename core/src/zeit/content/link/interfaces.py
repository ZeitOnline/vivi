# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interface definitions for the link content type."""

import zope.schema

import zeit.cms.content.interfaces
import zeit.content.image.interfaces.IImage
from zeit.cms.i18n import MessageFactory as _


class ILink(zope.interface.Interface):
    """A type for managing links to non-local content."""

    url = zope.schema.URI(title=_(u"Link address"))

    image = zope.schema.Object(
        zeit.content.image.interfaces.IImage)
