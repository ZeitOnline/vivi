# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import re
import zope.app.container.contained
import zope.app.container.interfaces
import zope.exceptions.interfaces
import zope.interface


invalid_chars = re.compile(r'[^a-z0-9\-]')


class NameChooser(zope.app.container.contained.NameChooser):

    zope.interface.implements(zope.app.container.interfaces.INameChooser)

    def __init__(self, context):
        self.context = context

    def checkName(self, name, object):
        super(NameChooser, self).checkName(name, object)
        m = invalid_chars.search(name)
        if m is not None:
            raise zope.exceptions.interfaces.UserError(
                "The given name contains invalid characters.")

    def chooseName(self, name, object):
        if isinstance(name, str):
            name = unicode(name)
        name = name.lower().replace(' ', '-')
        name = invalid_chars.sub('', name)
        return super(NameChooser, self).chooseName(name, object)
