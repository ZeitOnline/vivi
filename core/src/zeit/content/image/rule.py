from zeit.edit.rule import glob
import grokcore.component as grok
import zeit.content.image.interfaces
import zeit.edit.rule
import zope.interface


class ImageValidator(zeit.edit.rule.Validator):

    grok.context(zeit.content.image.interfaces.IImageGroup)


@glob(zope.interface.Interface)
def imagegroup(context):
    return False


@glob(zeit.content.image.interfaces.IImageGroup)
def imagegroup(context):
    return True


@glob(zope.interface.Interface)
def provided_scales(context):
    return []


@glob(zeit.content.image.interfaces.IImageGroup)
def provided_scales(context):
    scales = []
    for image in context.values():
        # Remove prefixed name of image group
        name = image.__name__.replace(context.__name__ + '-', '', 1)
        # Remove suffixed file type, e.g. ".jpg"
        name = name.rsplit('.', 1)[0]
        scales.append(name)
    return scales
