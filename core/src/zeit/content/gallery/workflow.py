# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.interface

import zeit.content.gallery.interfaces
import zeit.workflow.interfaces


class PublicationDependencies(object):
    """Gallery dependencies."""

    zope.interface.implements(
        zeit.workflow.interfaces.IPublicationDependencies)
    zope.component.adapts(
        zeit.content.gallery.interfaces.IGallery)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        if self.context.image_folder is not None:
            return (self.context.image_folder,)
        return ()
