# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.objectify
import urllib2
import zeit.cms.content.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zope.container.btree
import zope.interface


class Whitelist(zope.container.btree.BTreeContainer):

    # XXX this is only a toy implementation, see #8624
    # add tags for testing like this:
    # whitelist['mytag'] = zeit.cms.tagging.tag.Tag('mytag')

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    def search(self, prefix):
        result = []
        for tag in self.values():
            if tag.label.lower().startswith(prefix.lower()):
                result.append(tag)
        return result

    def _get_url(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        return cms_config.get('whitelist-url')

    def _fetch(self):
        return urllib2.urlopen(self._get_url())

    def _load(self):
        tags = {}
        tags_xml = gocept.lxml.objectify.fromfile(self._fetch())
        for tag_node in tags_xml.iterchildren('tag'):
            tag = zeit.cms.tagging.tag.Tag(
                tag_node.get('uuid'), unicode(tag_node).strip())
            tags[tag.code] = tag


class WhitelistSource(object):

    # this should be in .interfaces, but that leads to a circular import
    # between zeit.cms.content.interfaces and .interfaces

    zope.interface.implements(
        zeit.cms.tagging.interfaces.IWhitelistSource,
        zeit.cms.content.interfaces.IAutocompleteSource)

    @property
    def whitelist(self):
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)

    def __contains__(self, item):
        return item.code in self.whitelist

    def __iter__(self):
        return iter(self.whitelist.values())

    def get_check_types(self):
        """IAutocompleteSource"""
        return ['tag']
