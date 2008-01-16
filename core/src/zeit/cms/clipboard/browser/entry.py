# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.i18n
import zope.interface
import zope.publisher.interfaces

import zeit.cms.browser.interfaces
from  zeit.cms.i18n import MessageFactory as _

import zeit.cms.clipboard.interfaces



class Entry(object):

    def __call__(self):
        url = zope.traversing.browser.absoluteURL(self.context.references,
                                                  self.request)
        self.request.response.redirect(url + '/@@view.html')


class EntryListRepresentation(object):

    zope.interface.implements(
        zeit.cms.browser.interfaces.IListRepresentation)

    __name__ = None

    def __init__(self, context, name):
        self.context = context
        self.__name__ = name

    def __getattr__(self, key):
        return getattr(self.context, key)


class InvalidReferenceListRepresentation(object):

    zope.interface.implements(
        zeit.cms.browser.interfaces.IListRepresentation)

    author = None
    ressort = None
    searchableText = None
    page = None
    volume = None
    year = None
    workflowState = None
    modifiedBy = None
    url = None

    def __init__(self, request, unique_id):
        self.context = None
        self.request = request
        self.uniqueId = unique_id
        dummy, self.__name__  = unique_id.rsplit('/', 1)

    @property
    def title(self):
        title = _("Broken reference to ${uniqueId}",
                  mapping=dict(uniqueId=self.uniqueId))
        return zope.i18n.translate(title, context=self.request)

    def modifiedOn(format=None):
        return None

    def createdOn(format=None):
        return None


@zope.component.adapter(
    zeit.cms.clipboard.interfaces.IObjectReference,
    zope.publisher.interfaces.IPublicationRequest)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IListRepresentation)
def entryListRepresentationFactory(context, request):
    """Defer the list representation to the referenced object."""
    references = context.references
    if references is None:
        return InvalidReferenceListRepresentation(
            request, context.referenced_unique_id)
    list_repr = zope.component.getMultiAdapter(
        (references, request),
        zeit.cms.browser.interfaces.IListRepresentation)
    list_repr = EntryListRepresentation(list_repr, context.__name__)
    return list_repr


class DragPane(object):
    """Show drag pane of referenced object."""

    def __call__(self):
        return zope.component.getMultiAdapter(
            (self.context.references, self.request),
            name='drag-pane.html')()
