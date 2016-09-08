from zeit.cms.application import CONFIG_CACHE
import UserDict
import gocept.lxml.objectify
import logging
import urllib2
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zope.interface


log = logging.getLogger(__name__)


class Whitelist(UserDict.UserDict):

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    def __init__(self):
        # Super __init__ set's data attribute. The data attribute is replaced
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

    @CONFIG_CACHE.cache_on_arguments()
    def _load(self):
        tags = {}
        tags_xml = gocept.lxml.objectify.fromfile(self._fetch())
        for tag_node in tags_xml.xpath('//tag'):
            tag = zeit.cms.tagging.tag.Tag(
                tag_node.get('uuid'), unicode(tag_node).strip(),
                entity_type=tag_node.get('type'),
                url_value=tag_node.get('url_value'))
            tags[tag.code] = tag
        log.info('Keywords loaded.')
        return tags
