# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zope.component.zcml
import zope.configuration.fields
import zope.interface
import zope.security.metaconfigure


class IGlobsDirective(zope.interface.Interface):

    module = zope.configuration.fields.GlobalObject(
        title=u"Module containing globs")


def globs_directive(_context, module):
    for func, adapts in module._globs:
        zope.component.zcml.adapter(
            _context,
            for_=(adapts,),
            factory=(func,),
            provides=zeit.content.cp.interfaces.IRuleGlob,
            name=unicode(func.func_name))
