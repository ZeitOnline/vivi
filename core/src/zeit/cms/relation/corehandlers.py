# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import gocept.async
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zeit.cms.relation.interfaces
import zope.component
import zope.interface


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_index_on_checkin(context, event):
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relations.index(context)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def update_referencing_objects_handler(context, event):
    """Update metadata in objects which reference the checked-in object."""
    # prevent recursion
    if not gocept.async.is_async():
        update_referencing_objects(context)


@gocept.async.function('events')
def update_referencing_objects(context):
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relating_objects = relations.get_relations(context)
    for related_object in list(relating_objects):
        # the actual work is done by IBeforeCheckin-handlers
        zeit.cms.checkout.helper.with_checked_out(
            related_object, lambda x: True)
