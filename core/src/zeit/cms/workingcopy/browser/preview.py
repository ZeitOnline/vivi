# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import random
import urlparse
import sha

import zope.component

import zope.app.appsetup.product

import zeit.connector.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.browser.preview


class WorkingcopyPreview(zeit.cms.browser.preview.Preview):
    """Preview for workingcopy versions of content objects.

    Uploads the workingcopy version of an object to the repository, redirects
    the browser and schedules a removal job?
    """

    def __call__(self):
        # NOTE: the base-path is expected to exist
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        base = cms_config['workingcopy-preview-base']

        content = zeit.cms.interfaces.ICMSContent(
            zeit.connector.interfaces.IResource(self.context))

        temp_id = sha.new(content.uniqueId)
        temp_id.update(self.request.principal.id)
        temp_id.update(str(random.random()))

        unique_id = urlparse.urljoin(base, temp_id.hexdigest())
        content.uniqueId = unique_id

        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository.addContent(content)
        self.redirect_to_preview_of(content)
        return ''
