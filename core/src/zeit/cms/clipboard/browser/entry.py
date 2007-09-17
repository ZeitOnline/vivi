# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface
import zope.publisher.interfaces

import zeit.cms.browser.interfaces

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


@zope.component.adapter(
    zeit.cms.clipboard.interfaces.IObjectReference,
    zope.publisher.interfaces.IPublicationRequest)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IListRepresentation)
def entryListRepresentationFactory(context, request):
    """Defer the list representation to the referenced object."""
    references = context.references
    if references is None:
        return
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
