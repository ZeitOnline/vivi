import zope.interface
import zope.schema

from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.i18n import MessageFactory as _


class IGlobalSettings(zope.interface.Interface):
    """Global CMS settings."""

    default_year = zope.schema.Int(
        title=_('Default year'),
        min=ICommonMetadata['year'].min,
        max=ICommonMetadata['year'].max,
    )

    default_volume = zope.schema.Int(
        title=_('Default volume'),
        min=ICommonMetadata['volume'].min,
        max=ICommonMetadata['volume'].max,
    )

    def get_working_directory(template):
        """Return the collection which is the main working directory.

        template:
            Template which will be filled with year and volume. In
            ``template`` the placeholders $year and $volume will be replaced.
            Example: 'online/$year/$volume/foo'

        If the respective collection does not exist, it will be created before
        returning it.

        """
