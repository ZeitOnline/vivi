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
import zeit.cms.repository.folder
import zeit.cms.browser.preview


class WorkingcopyPreview(zeit.cms.browser.preview.Preview):
    """Preview for workingcopy versions of content objects.

    Uploads the workingcopy version of an object to the repository, redirects
    the browser and schedules a removal job?
    """

    def __call__(self):
        # NOTE: the base-path is expected to exist
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        base = cms_config['workingcopy-preview-base']

        # Make sure the base folder exists
        parsed_base = urlparse.urlparse(base)
        base_path = parsed_base[2]
        target_folder = repository
        for next_name in base_path.split('/'):
            if not next_name:
                # Ignore empty parts (i.e. start end end)
                continue
            if next_name not in target_folder:
                target_folder[next_name] = zeit.cms.repository.folder.Folder()
            target_folder = target_folder[next_name]

        # create a copy and remove unique id
        content = zeit.cms.interfaces.ICMSContent(
            zeit.connector.interfaces.IResource(self.context))
        unique_id = content.uniqueId
        content.uniqueId = None

        temp_id = sha.new(unique_id)
        temp_id.update(self.request.principal.id)
        temp_id.update(str(random.random()))
        temp_id = temp_id.hexdigest()

        target_folder[temp_id] = content
        self.redirect_to_preview_of(content)
        return ''
