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

    timeline_template = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'timeline_template', ITickarooLiveblog['timeline_template']
    )

    status = ObjectPathAttributeProperty('.', 'status', ITickarooLiveblog['status'])

    theme = ObjectPathAttributeProperty('.', 'theme', ITickarooLiveblog['theme'])
