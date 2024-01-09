import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.wysiwyg.interfaces


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def html_references(context):
    html_content = zeit.wysiwyg.interfaces.IHTMLContent(context, None)
    if html_content is None:
        return None
    return html_content.references
