# coding: utf8
# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zope.annotation.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.interface


class NoMetadata(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(zope.annotation.interfaces.IAttributeAnnotatable)
    default_template = '<empty/>'


NO_METADATA = NoMetadata()


class Details(zeit.cms.browser.view.Base):
    """Render details about an content object."""

    @zope.cachedescriptors.property.Lazy
    def list_repr(self):
        return zope.component.queryMultiAdapter(
            (self.context, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)

    @zope.cachedescriptors.property.Lazy
    def common_metadata(self):
        return zeit.cms.content.interfaces.ICommonMetadata(
            self.context, NO_METADATA)

    @property
    def teaser_title(self):
        if self.common_metadata is not NO_METADATA:
            return self.common_metadata.teaserTitle
        if self.list_repr is not None:
            return self.list_repr.title

    @property
    def preview_url(self):
        return zope.component.queryMultiAdapter(
            (self.context, 'preview'),
            zeit.cms.browser.interfaces.IPreviewURL)

    @zope.cachedescriptors.property.Lazy
    def graphical_preview_url(self):
        thumbnail = zope.component.queryMultiAdapter(
            (self.context, self.request), name='thumbnail')
        if thumbnail is None:
            return
        return self.url('@@thumbnail')

    @property
    def author(self):
        if self.common_metadata is NO_METADATA:
            return
        if self.common_metadata.author_references:
            return self.common_metadata.author_references[0].display_name
        elif self.common_metadata.authors:
            return self.common_metadata.authors[0]

    @zope.cachedescriptors.property.Lazy
    def countings(self):
        return zeit.cms.content.interfaces.IAccessCounter(self.context, None)

    @property
    def hits(self):
        if self.countings is None:
            return
        return '%s/%s' % (
            self.countings.hits or 0, self.countings.total_hits or 0)

    def display_metadata(self):
        return filter(None, [
                'XXX Datum',
                'XXX Ausgabe',
                self.common_metadata.ressort,
                self.author,
                self.hits,
                ])
