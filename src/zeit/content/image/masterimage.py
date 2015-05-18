import grokcore.component as grok
import zeit.cms.interfaces
import zeit.content.image.interfaces


@grok.adapter(zeit.content.image.interfaces.IRepositoryImageGroup)
@grok.implementer(zeit.content.image.interfaces.IMasterImage)
def repository_group_to_master(context):
    if context.master_image:
        return context.get(context.master_image)


@grok.adapter(zeit.content.image.interfaces.ILocalImageGroup)
@grok.implementer(zeit.content.image.interfaces.IMasterImage)
def local_group_to_master(context):
    return zeit.content.image.interfaces.IMasterImage(
        zeit.cms.interfaces.ICMSContent(context.uniqueId))
