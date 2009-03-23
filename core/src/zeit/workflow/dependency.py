# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Publication dependencies."""

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.dublincore.interfaces
import zope.interface


class Dependencies(object):
    """Adapter to find the publication dependencies of an object."""

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        dependencies = set()
        for name, this_deps in zope.component.getAdapters(
            (self.context, ),
            zeit.workflow.interfaces.IPublicationDependencies):
            if not name:
                # This is actually this adapter
                continue
            dependencies.update(this_deps.get_dependencies())
        return sorted(dependencies, key=lambda x: x.uniqueId)


class Relateds(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        relateds = zeit.cms.related.interfaces.IRelatedContent(self.context,
                                                               None)
        if relateds is None:
            return []
        dependencies = []
        for related in relateds.related:
            workflow = zeit.cms.workflow.interfaces.IPublishInfo(related)
            dc = zope.dublincore.interfaces.IDCTimes(related)
            sc = zeit.cms.content.interfaces.ISemanticChange(related)

            if not workflow.published:
                continue
            if not all((sc.last_semantic_change,
                        workflow.date_last_published,
                        dc.modified)):
                continue
            if not (sc.last_semantic_change
                    < workflow.date_last_published
                    < dc.modified):
                continue
            dependencies.append(related)
        return dependencies
