# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urlparse

import zope.app.appsetup.product

import zeit.cms.interfaces


class PreviewBase(object):

    def __call__(self):
        unique_id = self.context.uniqueId
        path = unique_id[len(zeit.cms.interfaces.ID_NAMESPACE):]
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        prefix = cms_config[self.prefix]
        if not prefix.endswith('/'):
            prefix = prefix + '/'
        url = urlparse.urljoin(prefix, path)
        self.request.response.redirect(url)
        return ''


class Preview(PreviewBase):

    prefix = 'preview-prefix'


class Live(PreviewBase):

    prefix = 'live-prefix'


class DevelopmentPreview(PreviewBase):

    prefix = 'development-preview-prefix'
