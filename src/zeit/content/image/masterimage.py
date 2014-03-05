# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.image.interfaces
import zope.component
import zope.interface


@zope.interface.implementer(zeit.content.image.interfaces.IMasterImage)
@zope.component.adapter(zeit.content.image.interfaces.IImageGroup)
def group_to_master(context):
    if context.master_image:
        return context.get(context.master_image)
