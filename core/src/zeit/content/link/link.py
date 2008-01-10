# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Implementation of the link content type."""

import zope.interface

import zeit.cms.content.metadata
import zeit.cms.content.property

import zeit.content.link.interfaces


class Link(zeit.cms.content.metadata.CommonMetadata):
    """A type for managing links to non-local content."""

    zope.interface.implements(zeit.content.link.interfaces.ILink)

    default_template = "<link><head/><body/></link>"

    url = zeit.cms.content.property.ObjectPathProperty('.body.url')
