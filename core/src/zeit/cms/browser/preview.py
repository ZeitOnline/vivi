# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urlparse

import zope.app.appsetup.product

import zeit.cms.interfaces
import zeit.cms.browser.interfaces
import zeit.cms.browser.view


def get_preview_url(prefix, unique_id):
    """Given a prefix and a unique id, return preview URL.
    """
    path = unique_id[len(zeit.cms.interfaces.ID_NAMESPACE):]
    cms_config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.cms')
    prefix = cms_config[prefix]
    if not prefix.endswith('/'):
        prefix = prefix + '/'
    return urlparse.urljoin(prefix, path)
    
class PreviewBase(zeit.cms.browser.view.Base):
    """Base class for preview."""

    def get_preview_url_for(self, preview_context):
        unique_id = preview_context.uniqueId
        return get_preview_url(self.prefix, unique_id)

    def __call__(self):
        preview_object = zeit.cms.browser.interfaces.IPreviewObject(
            self.context, self.context)
        self.redirect(self.get_preview_url_for(preview_object))
        return ''


class Preview(PreviewBase):

    prefix = 'preview-prefix'


class Live(PreviewBase):

    prefix = 'live-prefix'


class DevelopmentPreview(PreviewBase):

    prefix = 'development-preview-prefix'
