# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Implementation of the link content type."""

import zeit.cms.content.base


class Link(zeit.cms.content.base.ContentBase):
    """A type for managing links to non-local content."""

    zope.interface.implements(zeit.content.link.interfaces.ILink)

    default_template = "<link>\n\t<url/>\n\t<image/>\n</link>"

    url = zeit.cms.content.property.ObjectPathProperty(
        XXXnamespace, '.link.url')

    image = zeit.cms.content.property.ImageProperty()
