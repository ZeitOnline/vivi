# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import gocept.cache.method
import gocept.lxml.objectify
import grokcore.component as grok
import urllib2
import zeit.cms.content.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zope.interface


class Whitelist(UserDict.UserDict,
                grok.GlobalUtility):

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    def __init__(self):
        # Super __init__ set's data attribute. The data attribute is repalced
        # with a property here, breaking the super __init__.
        pass

    @property
    def data(self):
        return self._load()

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
        url = self._get_url()
        __traceback_info__ = (url,)
        return urllib2.urlopen(url)

    @gocept.cache.method.Memoize(600)
    def _load(self):
        tags = {}
        tags_xml = gocept.lxml.objectify.fromfile(self._fetch())
        for tag_node in tags_xml.iterchildren('tag'):
            tag = zeit.cms.tagging.tag.Tag(
                tag_node.get('uuid'), unicode(tag_node).strip())
            tags[tag.code] = tag
        return tags


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
