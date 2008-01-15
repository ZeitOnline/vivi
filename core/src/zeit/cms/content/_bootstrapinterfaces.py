# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Extra module to prevent circular imports."""

import zope.interface
import zope.schema


class ICMSContentSource(zope.schema.interfaces.ISource):
    """A source for CMS content types."""

    name = zope.interface.Attribute("Utility name of the source")
