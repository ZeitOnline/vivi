# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import lxml.etree

import zope.interface
import zope.component

import z3c.flashmessage.interfaces

import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.relation.interfaces
from zeit.cms.i18n import MessageFactory as _


log= logging.getLogger(__name__)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_index_on_checkin(context, event):
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relations.index(context)

def with_checked_out(content, function):
    """Call a function with a checked out version of content.

    Function makes sure content is checked back in after the function ran.

    """
    # XXX should be moved to some central place.
    manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
    if not manager.canCheckout:
        # XXX test this path!
        # XXX this warning should be displayed to the user ASAP.
        log.warning("Could not checkout %s for related update." %
                       content.uniqueId)
        source = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource, name='session')
        source.send(
            _('Could not checkout "${id}" for automatic object update.',
              mapping=dict(id=content.uniqueId)),
            'error')
        return
    checked_out = manager.checkout(temporary=True)

    changed = function(checked_out)

    if changed:
        manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
        manager.checkin()
    else:
        del checked_out.__parent__[checked_out.__name__]


def update_relating_of_checked_out(checked_out):
    """Update the objects which relate the checked_out."""
    related = zeit.cms.content.interfaces.IRelatedContent(
        checked_out, None)
    if related is None:
        return False

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
        return False

    return True


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def update_relating(context, event):
    """Update metadata in object which relates another."""
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relating_objects = relations.get_relations(context, 'related')
    for related_object in relating_objects:
        with_checked_out(related_object, update_relating_of_checked_out)
