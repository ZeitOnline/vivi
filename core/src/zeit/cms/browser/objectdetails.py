# coding: utf8
# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zope.cachedescriptors.property
import zope.component
import zope.viewlet.interfaces


class IViewlets(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for object details."""


class Details(zeit.cms.browser.view.Base):
    """Render details about an content object."""

    @zope.cachedescriptors.property.Lazy
    def list_repr(self):
        return zope.component.queryMultiAdapter(
            (self.context, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)

    @zope.cachedescriptors.property.Lazy
    def common_metadata(self):
        return zeit.cms.content.interfaces.ICommonMetadata(self.context, None)

    @property
    def teaser_title(self):
        if self.common_metadata is not None:
            return self.common_metadata.teaserTitle
        if self.list_repr is not None:
            return self.list_repr.title

    @property
    def supertitle(self):
        if self.common_metadata is not None:
            return self.common_metadata.supertitle

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
