# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

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

    def get_unique_id(self):
        return self.context.references.uniqueId


class AjaxDeleteEntry(object):

    def delete(self):
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(self.context)
        del self.context.__parent__[self.context.__name__]
        tree = zope.component.getMultiAdapter((clipboard, self.request),
                                              name="tree.html")
        return tree()


class EntryListRepresentation(object):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)

    __name__ = None
    type = 'reference'

    def __init__(self, context, list_repr, name):
        self.context = context
        self.list_repr = list_repr
        self.__name__ = name

    def __getattr__(self, key):
        return getattr(self.list_repr, key)

    @zope.cachedescriptors.property.Lazy
    def url(self):
        return zope.component.getMultiAdapter(
            (self.context, self.request),
            name='absolute_url')


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
    type = 'unknown'

    modifiedOn = createdOn = None

    def __init__(self, request, unique_id):
        self.context = None
        self.request = request
        self.uniqueId = unique_id
        dummy, self.__name__ = unique_id.rsplit('/', 1)

    @property
    def title(self):
        title = _("Broken reference to ${uniqueId}",
                  mapping=dict(uniqueId=self.uniqueId))
        return zope.i18n.translate(title, context=self.request)


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
    list_repr = zope.component.queryMultiAdapter(
        (references, request),
        zeit.cms.browser.interfaces.IListRepresentation)
    if list_repr is None:
        return None
    list_repr = EntryListRepresentation(context, list_repr, context.__name__)
    return list_repr


class DragPane(object):
    """Show drag pane of referenced object."""

    def __call__(self):
        return zope.component.getMultiAdapter(
            (self.context.references, self.request),
            name='drag-pane.html')()


@zope.component.adapter(
    zeit.cms.clipboard.interfaces.IObjectReference,
    zope.publisher.interfaces.browser.IBrowserRequest)
@zope.interface.implementer(zope.interface.Interface)
def entry_icon(context, request):
    references = context.references
    if references is None:
        return None
    return zope.component.queryMultiAdapter(
        (references, request), name="zmi_icon")
