# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Remove old in-ram image instances."""

import zope.component

import zeit.cms.generation
import zeit.cms.workingcopy.interfaces
import zeit.content.image.image


@zeit.cms.generation.get_root
def evolve(root):
    workingcopy_location = zope.component.getUtility(
        zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)

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
