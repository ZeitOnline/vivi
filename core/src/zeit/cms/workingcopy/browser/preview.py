# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urlparse
import urllib2
import sha

import zope.cachedescriptors.property
import zope.component

import zope.app.appsetup.product

import zeit.connector.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.folder
import zeit.cms.browser.preview


class WorkingcopyPreview(zeit.cms.browser.preview.Preview):
    """Preview for workingcopy versions of content objects.

    Uploads the workingcopy version of an object to the repository, retrieves
    the html and returns it.

    """

    def __call__(self):
        preview_obj = self.get_preview_object()
        url = self.get_preview_url_for(preview_obj)
        preview_request = urllib2.urlopen(url)
        del preview_obj.__parent__[preview_obj.__name__]
        return preview_request.read()

    def get_preview_url_for(self, preview_context):
        url = super(WorkingcopyPreview, self).get_preview_url_for(preview_context)
        url = '%s?%s' % (url, self.request.environment['QUERY_STRING'])
        return url

    def get_preview_object(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        base = cms_config['workingcopy-preview-base']

        # Make sure the base folder exists
        parsed_base = urlparse.urlparse(base)
        base_path = parsed_base[2]
        target_folder = self.repository
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

        temp_id = self.get_temp_id(unique_id)
        target_folder[temp_id] = content
        return content

    def get_temp_id(self, unique_id):
        temp_id = sha.new(unique_id)
        temp_id.update(self.request.principal.id)
        temp_id = temp_id.hexdigest()
        return temp_id

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
