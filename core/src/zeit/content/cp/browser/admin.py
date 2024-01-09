import grokcore.component as grok

import zeit.cms.admin.interfaces
import zeit.content.cp.interfaces


@grok.adapter(zeit.content.cp.interfaces.ICenterPage, name='zeit.content.cp')
@grok.implementer(zeit.cms.admin.interfaces.IAdditionalFieldsCO)
def additional_fields_co(context):
    return (zeit.content.cp.interfaces.ICenterPage, ['year'])
