# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.app.container.interfaces
import zope.component
import zope.interface


@zope.component.adapter(
    zeit.cms.repository.interfaces.IFolder,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def folder_default_browse_location(context, source):
    return context


@zope.component.adapter(
    zope.app.container.interfaces.IContained,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def content_default_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


class ObjectBrowser(zeit.cms.browser.listing.Listing):
    """Objectbrowser."""

    def __call__(self):
        self.request.form['autoexpand-tree'] = True
        return super(ObjectBrowser, self).__call__()

    def filter_content(self, obj):
        if self.filter_source is not None:
            return obj in self.filter_source
        return True

    @zope.cachedescriptors.property.Lazy
    def filter_source(self):
        source_name = self.request.get('type_filter')
        if not source_name:
            return None
        return zope.component.getUtility(
            zeit.cms.content.interfaces.ICMSContentSource,
            name=source_name)


class BrowsingLocation(zeit.cms.browser.view.Base):

    def __call__(self, type_filter):
        source = zope.component.getUtility(
            zeit.cms.content.interfaces.ICMSContentSource,
            name=type_filter)
        location = zope.component.queryMultiAdapter(
            (self.context, source),
            zeit.cms.browser.interfaces.IDefaultBrowsingLocation)

        self.redirect(self.url(
            location, '@@get_object_browser?type_filter=%s' % type_filter))
        return ''
