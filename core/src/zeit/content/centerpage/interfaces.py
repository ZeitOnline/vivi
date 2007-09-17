
# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zeit.cms.interfaces
import zeit.cms.content.interfaces

class ICenterPageMetadata(zeit.cms.content.interfaces.ICommonMetadata):
    """Cennter page metadata."""

class ICenterPage(ICenterPageMetadata,
                  zeit.cms.content.interfaces.IXMLContent):
    """A center page"""
