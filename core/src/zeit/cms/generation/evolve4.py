# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces


def update(root):
    # Change the storage type of hidden containers from zc.set to TreeSet
    # We don't migtrate the user preferences here but just remove it.
    workingcopy_location = zope.component.getUtility(
        zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
    for name in workingcopy_location:
        workingcopy = workingcopy_location[name]
        prefs = zeit.cms.repository.interfaces.IUserPreferences(workingcopy)
        prefs.__init__()


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
