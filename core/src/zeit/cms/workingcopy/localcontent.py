# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.workingcopy.interfaces.ILocalContent)
def default_local_content_adapter(context):
    # Default adapter to adapt cms content to local content: create a copy and
    # mark as local content
    if zeit.cms.repository.interfaces.ICollection.providedBy(context):
        # We cannot checkout containers. Special treat is required for them.
        return None
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    content = repository.getCopyOf(context.uniqueId)
    zope.interface.directlyProvides(
        content, zeit.cms.workingcopy.interfaces.ILocalContent)
    return content


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.repository.interfaces.IRepositoryContent)
def default_repository_content_adapter(context):
    # Default adapter to adapt local content to repository content: add to
    # repository and return
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository.addContent(context)
    added = repository.getContent(context.uniqueId)
    return added
