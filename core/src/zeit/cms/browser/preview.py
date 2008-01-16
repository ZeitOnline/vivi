# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urlparse

import zope.app.appsetup.product

import zeit.cms.interfaces


class PreviewBase(object):

    def redirect_to_preview_of(self, preview_context):
        unique_id = preview_context.uniqueId
        path = unique_id[len(zeit.cms.interfaces.ID_NAMESPACE):]
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        prefix = cms_config[self.prefix]
        if not prefix.endswith('/'):
            prefix = prefix + '/'
        url = urlparse.urljoin(prefix, path)
        self.request.response.redirect(url)

    def __call__(self):
        self.redirect_to_preview_of(self.context)
        return ''


class Preview(PreviewBase):

    prefix = 'preview-prefix'


class Live(PreviewBase):

    prefix = 'live-prefix'


class DevelopmentPreview(PreviewBase):

    prefix = 'development-preview-prefix'
