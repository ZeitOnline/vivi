# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import lxml.etree

import zope.interface
import zope.component

import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.relation.interfaces


logger = logging.getLogger(__name__)


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
def update_relating(context, event):
    """Update metadata in object which relates another."""
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relating_objects = relations.get_relations(context, 'related')
    for related_object in relating_objects:
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(
            related_object)
        if not manager.canCheckout:
            logger.warning("Could not checkout %s for related update." %
                           related_object.uniqueId)
            continue
        checked_out = manager.checkout()
        related = zeit.cms.content.interfaces.IRelatedContent(
            checked_out, None)
        if related is None:
            del checked_out.__parent__[checked_out.__name__]
            continue

        # Get an xml representation of the related to check if anything was
        # actually changed
        xml_before = lxml.etree.tostring(
            zeit.cms.content.interfaces.IXMLRepresentation(related).xml)

        # Update related
        related.related = related.related

        # Make sure there actually was a change.
        xml_after = lxml.etree.tostring(
            zeit.cms.content.interfaces.IXMLRepresentation(related).xml)

        if xml_before == xml_after:
            del checked_out.__parent__[checked_out.__name__]
        else:
            manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
            manager.checkin()
