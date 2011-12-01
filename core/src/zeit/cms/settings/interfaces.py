# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.schema


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

    def get_working_directory(template):
        """Return the collection which is the main working directory.

        template:
            Template which will be filled with year and volume. In
            ``template`` the placeholders $year and $volume will be replaced.
            Example: 'online/$year/$volume/foo'

        If the respective collection does not exist, it will be created before
        returning it.

        """
