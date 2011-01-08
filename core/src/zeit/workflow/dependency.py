# Copyright (c) 2008-2011 gocept gmbh & co. kg
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


def has_only_non_semantic_changes(content):
    """Returns if content has changes but only non sematincally ones.

    When True is returned this usually means content can be published without
    further notice. This also includes that it has been published before.

    """
    workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
    dc = zope.dublincore.interfaces.IDCTimes(content)
    sc = zeit.cms.content.interfaces.ISemanticChange(content)
    if not workflow.published:
        return False
    if not all((sc.last_semantic_change,
                workflow.date_last_published,
                dc.modified)):
        # We have not all values for comparison. Be on the save side.
        return False
    if not (sc.last_semantic_change
            <= workflow.date_last_published
            <= dc.modified):
        return False
    return True


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
            if has_only_non_semantic_changes(related):
                dependencies.append(related)
        return dependencies
