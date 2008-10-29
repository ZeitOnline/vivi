# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _

class IGlobalSettings(zope.interface.Interface):
    """Global CMS settings."""

    default_year = zope.schema.Int(
        title=_("Default year"),
        min=1900,
        max=2100)

    default_volume = zope.schema.Int(
        title=_("Default volume"),
        min=1,
        max=53)
