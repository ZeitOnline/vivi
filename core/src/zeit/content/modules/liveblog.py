import zope.interface

from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.content.modules.interfaces import ITickarooLiveblog
import zeit.edit.block


@zope.interface.implementer(zeit.content.modules.interfaces.ITickarooLiveblog)
class TickarooLiveblog(zeit.edit.block.Element):
    liveblog_id = ObjectPathAttributeProperty('.', 'liveblog_id', ITickarooLiveblog['liveblog_id'])

    collapse_preceding_content = ObjectPathAttributeProperty(
        '.', 'collapse_preceding_content', ITickarooLiveblog['collapse_preceding_content']
    )

    show_timeline_in_teaser = ObjectPathAttributeProperty(
        '.', 'show_timeline_in_teaser', ITickarooLiveblog['show_timeline_in_teaser']
    )

    status = ObjectPathAttributeProperty('.', 'status', ITickarooLiveblog['status'])

    theme = ObjectPathAttributeProperty('.', 'theme', ITickarooLiveblog['theme'])

    intersection_type = ObjectPathAttributeProperty(
        '.', 'intersection_type', ITickarooLiveblog['intersection_type']
    )
