import grokcore.component as grok
import zeit.cms.admin.interfaces
import zeit.content.dynamicfolder.interfaces


@grok.adapter(zeit.content.dynamicfolder.interfaces.IRepositoryDynamicFolder)
@grok.implementer(zeit.cms.admin.interfaces.IAdditionalFields)
def additional_fields_ci(context):
    return (zeit.content.dynamicfolder.interfaces.ICloneArmy, ['activate'])
