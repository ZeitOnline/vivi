# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zope.component


class AddPlaceHolder(object):

    def __call__(self):
        factory = zope.component.getAdapter(
            self.context, zeit.content.cp.interfaces.IBoxFactory,
            name='placeholder')
        factory()


class PlaceHolderEdit(object):
    pass
