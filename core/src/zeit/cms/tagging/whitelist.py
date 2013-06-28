# Copyright (c) 2011-2013 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import gocept.cache.method
import gocept.lxml.objectify
import grokcore.component as grok
import logging
import urllib2
import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zeit.cms.content.contentsource
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zope.interface


log = logging.getLogger(__name__)


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

    def search(self, term):
        term = term.lower()
        return [tag for tag in self.values() if term in tag.label.lower()]

    def _get_url(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        return cms_config.get('whitelist-url')

    def _fetch(self):
        url = self._get_url()
        __traceback_info__ = (url,)
        log.info('Loading keyword whitelist from %s', url)
        return urllib2.urlopen(url)

    @gocept.cache.method.Memoize(600, ignore_self=True)
    def _load(self):
        tags = {}
        tags_xml = gocept.lxml.objectify.fromfile(self._fetch())
        for tag_node in tags_xml.iterchildren('tag'):
            tag = zeit.cms.tagging.tag.Tag(
                tag_node.get('uuid'), unicode(tag_node).strip())
            tags[tag.code] = tag
        log.info('Keywords loaded.')
        return tags


class WhitelistSource(
        zc.sourcefactory.contextual.BasicContextualSourceFactory):

    # this should be in .interfaces, but that leads to a circular import
    # between zeit.cms.content.interfaces and .interfaces

    # this is only contextual so we can customize the source_class

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        zope.interface.implements(
            zeit.cms.tagging.interfaces.IWhitelistSource,
            zeit.cms.content.contentsource.IAutocompleteSource)

        def get_check_types(self):
            """IAutocompleteSource"""
            return ['tag']

        def __contains__(self, value):
            # XXX we need our own equality check here: we can't use Tag.__eq__,
            # since that has a specific meaning only useful for formlib
            if not hasattr(value, 'code'):
                return False
            for tag in self._get_filtered_values():
                if tag.code == value.code:
                    return True

    @property
    def whitelist(self):
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)

    def getValues(self, context):
        return self.whitelist.values()

    def getTitle(self, context, value):
        return value.label

    def getToken(self, context, value):
        return value.code
