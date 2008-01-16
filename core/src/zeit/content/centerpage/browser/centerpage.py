# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os

import zope.component
import zope.publisher.interfaces

import zeit.cms.browser.listing
import zeit.cms.browser.interfaces
import zeit.xmleditor.browser.editor
import zeit.content.centerpage.interfaces


class ListRepresentation(
    zeit.cms.browser.listing.CommonListRepresentation):
    """Adapter for listing centerpage resources"""

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.content.centerpage.interfaces.ICenterPage,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def metadata(self):
        url = zope.traversing.browser.absoluteURL(self, self.request)
        id = self.context.__name__
        return ('<span class="Metadata">%s/metadata_preview</span><span'
                ' class="DeleteId">%s</span>' %(url, id))


xi_include = '{http://www.w3.org/2001/XInclude}include'

class XMLEditor(zeit.xmleditor.browser.editor.Editor):

    CHILDREN = {
        'body': ('column', 'row', xi_include),
        'column': ('container', 'block'),
        'row': ('container', 'block', xi_include),
        'container': ('block', 'title',),
        'block': ('block', 'line', 'feed', 'ad', 'raw', 'title', 'byline',
                  'supertitle', 'text', 'image'),
    }

    XSLT = os.path.join(os.path.dirname(__file__), 'centerpage.xslt')
