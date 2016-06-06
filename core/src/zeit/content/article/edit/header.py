import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.edit.container
import zope.component


HEADER_NAME = 'editable-header'


class HeaderArea(zeit.edit.container.Base,
                 grok.MultiAdapter):

    grok.implements(zeit.content.article.edit.interfaces.IHeaderArea)
    grok.provides(zeit.content.article.edit.interfaces.IHeaderArea)
    grok.adapts(zeit.content.article.interfaces.IArticle,
                gocept.lxml.interfaces.IObjectified)

    __name__ = HEADER_NAME

    _find_item = lxml.etree.XPath(
        './/*[@cms:__name__ = $name]',
        namespaces=dict(
            cms='http://namespaces.zeit.de/CMS/cp'))

    def _get_element_type(self, xml_node):
        return xml_node.tag

    def insert(self, position, item):
        self._clear()
        return super(HeaderArea, self).insert(position, item)

    def add(self, item):
        self._clear()
        return super(HeaderArea, self).add(item)

    def _clear(self):
        for key in list(self.keys()):
            self._delete(key)

    def _set_default_key(self, xml_node):
        # XXX copy&paste from .body.Body
        key = xml_node.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        if not key:
            key = self._generate_block_id()
            xml_node.set('{http://namespaces.zeit.de/CMS/cp}__name__', key)
            self._p_changed = True
        return key

    def _get_keys(self, xml_node):
        result = []
        for child in xml_node.iterchildren():
            result.append(self._set_default_key(child))
        return result

    def values(self):
        # We re-implement values() so it works without keys(), since those are
        # not present in the repository.
        result = []
        for child in self.xml.iterchildren():
            element = self._get_element_for_node(child)
            if element is None:
                element = self._get_element_for_node(
                    child, zeit.edit.block.UnknownBlock.type)
            result.append(element)
        return result

    @property
    def module(self):
        values = self.values()
        if not values:
            return None
        return values[0]


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.content.article.edit.interfaces.IHeaderArea)
def get_header_area(article):
    node = article.xml.xpath('//head/header')
    if not node:
        article.xml['head'].append(lxml.objectify.E.header())
    node = article.xml.xpath('//head/header')[0]
    return zope.component.queryMultiAdapter(
        (article,
         zope.security.proxy.removeSecurityProxy(node)),
        zeit.content.article.edit.interfaces.IHeaderArea)


class ModuleSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'header-module-source'
    attribute = 'id'

    # For consistency with the zeit.content.cp config files.
    def _get_title_for(self, node):
        return unicode(node.get('title'))

MODULES = ModuleSource()
