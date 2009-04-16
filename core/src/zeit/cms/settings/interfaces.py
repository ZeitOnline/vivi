# Copyright (c) 2008-2009 gocept gmbh & co. kg
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

    def get_online_working_directory():
        """Return the collection which is the main working directory.

        This is /online/year/volume. If that collection does not exist, it will
        be created before returning it.

        """
