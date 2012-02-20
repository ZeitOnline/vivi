# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.whitelist


def update(root):
    utility = root['tag-whitelist']
    site_manager = zope.component.getSiteManager()
    site_manager.unregisterUtility(utility, interface, name=utility_name)
    del root['tag-whitelist']


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
