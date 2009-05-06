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

    def get_working_directory(prefix):
        """Return the collection which is the main working directory.

        prefix: sequence of path elements to prefix. A prefix of ('online',)
        results in /online/year/volume.

        If the respective collection does not exist, it will be created before
        returning it.

        """
