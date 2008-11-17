# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urlparse
import urllib2
import time

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
        url = super(WorkingcopyPreview, self).get_preview_url_for(
            preview_context)
        url = '%s?%s' % (url, self.request.environment['QUERY_STRING'])
        return url

    def get_preview_object(self):
        # create a copy and remove unique id
        content = zeit.cms.interfaces.ICMSContent(
            zeit.connector.interfaces.IResource(self.context))
        unique_id = content.uniqueId
        content.uniqueId = None

        target_folder = self.repository.getContent(
            self.context.uniqueId).__parent__

        temp_id = self.get_temp_id(self.context.__name__)
        target_folder[temp_id] = content
        return content

    def get_temp_id(self, name):
        return 'preview-%s-%s' % (
            self.request.principal.id, name)

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
