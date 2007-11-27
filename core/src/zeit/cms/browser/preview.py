# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urlparse

import zeit.cms.config
import zeit.cms.interfaces


class PreviewBase(object):

    def __call__(self):
        unique_id = self.context.uniqueId
        path = unique_id[len(zeit.cms.interfaces.ID_NAMESPACE):]
        prefix = self.prefix
        if not prefix.endswith('/'):
            prefix = prefix + '/'
        url = urlparse.urljoin(prefix, path)
        self.request.response.redirect(url)
        return ''


class Preview(PreviewBase):

    prefix = zeit.cms.config.PREVIEW_PREFIX


class Live(PreviewBase):

    prefix = zeit.cms.config.LIVE_PREFIX


class DevelopmentPreview(PreviewBase):

    prefix = zeit.cms.config.DEVELOPMENT_PREVIEW_PREFIX
