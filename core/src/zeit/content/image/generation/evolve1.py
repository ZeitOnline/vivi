import zeit.cms.generation
import zeit.cms.workingcopy.interfaces
import zeit.content.image.image
import zope.component


def update(root):
    workingcopy_location = zope.component.getUtility(
        zeit.cms.workingcopy.interfaces.IWorkingcopyLocation
    )

    for workingcopy in workingcopy_location.values():
        for name in list(workingcopy):
            image = workingcopy[name]
            if not isinstance(image, zeit.content.image.image.Image):
                continue
            new_image = zeit.content.image.image.LocalImage()
            new_image.open('w').write(image.data)
            new_image.mimeType = image.contentType
            new_image.__annotations__ = image.__annotations__
            new_image.__name__ = name
            new_image.__parent__ = workingcopy
            new_image.uniqueId = image.uniqueId
            # Sneak in the new object
            workingcopy._SampleContainer__data[name] = new_image


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
