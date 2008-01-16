# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.clipboard.entry
import zeit.cms.workingcopy.interfaces

@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.ICheckinEvent)
def add_ghost_after_checkin(context, event):
    workingcopy = zeit.cms.workingcopy.interfaces.IWorkingcopy(
        event.principal)
    entry = zeit.cms.clipboard.entry.Entry(context)
    zope.interface.directlyProvides(
        entry, zeit.cms.workingcopy.interfaces.ILocalContent)
    chooser = zope.app.container.interfaces.INameChooser(workingcopy)
    name = chooser.chooseName(context.__name__, entry)
    workingcopy[name] = entry
