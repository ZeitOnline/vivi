# coding: utf8
# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zope.annotation.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.dublincore.interfaces
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
    def teaser_text(self):
        if self.common_metadata is not NO_METADATA:
            return self.common_metadata.teaserText

    @property
    def preview_url(self):
        return zope.component.queryMultiAdapter(
            (self.context, 'preview'),
            zeit.cms.browser.interfaces.IPreviewURL)

    @property
    def live_url(self):
        return zope.component.queryMultiAdapter(
            (self.context, 'live'),
            zeit.cms.browser.interfaces.IPreviewURL)

    @property
    def resources_filename(self):
        urlstring = zope.component.queryMultiAdapter(
            (self.context, 'live'),
            zeit.cms.browser.interfaces.IPreviewURL)
        return urlstring.split('/')[-1]

    @zope.cachedescriptors.property.Lazy
    def graphical_preview_url(self):
        thumbnail = zope.component.queryMultiAdapter(
            (self.context, self.request), name='thumbnail')
        if thumbnail is None:
            return
        return self.url('@@thumbnail')

    @zope.cachedescriptors.property.Lazy
    def large_graphical_preview_url(self):
        thumbnail = zope.component.queryMultiAdapter(
            (self.context, self.request), name='thumbnail_large')
        if thumbnail is None:
            return
        return self.url('@@thumbnail_large')

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

    @property
    def volume(self):
        year = self.common_metadata.year
        vol = self.common_metadata.volume
        if year is None:
            return
        return (vol and '%s/%s' % (vol, year)) or '%s' % (year)

    @property
    def display_metadata(self):
        dc = zope.dublincore.interfaces.IDCTimes(self.context)
        entries = dict(
            teaser_title=self.teaser_title,
            created=dc.created and dc.created.strftime('%d.%m.%Y'),
            ressort=self.common_metadata.ressort,
            author=self.author,
            volume=self.volume,
            hits=self.hits,
        )
        for key, value in entries.items():
            if not value:
                del entries[key]
        return entries

    def display_metadata_short(self):
        dc = zope.dublincore.interfaces.IDCTimes(self.context)
        return filter(None, [
            dc.created and dc.created.strftime('%d.%m.%Y'),
            self.common_metadata.ressort,
            self.author,
            self.volume,
            self.hits,
        ])

    @property
    def type_declaration(self):
        no_type = type(
            'NoTypeDeclaration', (object,), dict(type_identifier='unknown'))
        return zeit.cms.interfaces.ITypeDeclaration(self.context, no_type)
