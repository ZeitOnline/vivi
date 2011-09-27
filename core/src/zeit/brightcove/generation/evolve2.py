# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.brightcove.interfaces
import zeit.cms.generation
import zope.component


def update(root):
    # Remove the brightcove repository from ZODB
    repository = zope.component.queryUtility(
        zeit.brightcove.interfaces.IRepository)
    if repository is not None:
        site_manager = zope.component.getSiteManager()
        site_manager.unregisterUtility(
            repository,
            zeit.brightcove.interfaces.IRepository)
        del repository.__parent__[repository.__name__]

def evolve(context):
    zeit.cms.generation.do_evolve(context, update)

