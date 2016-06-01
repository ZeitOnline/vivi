import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.edit.container
import zope.component


HEADER_NAME = 'editable-header'


class HeaderArea(zeit.edit.container.TypeOnAttributeContainer,
                 grok.MultiAdapter):

    grok.implements(zeit.content.article.edit.interfaces.IHeaderArea)
    grok.provides(zeit.content.article.edit.interfaces.IHeaderArea)
    grok.adapts(zeit.content.article.interfaces.IArticle,
                gocept.lxml.interfaces.IObjectified)

    __name__ = HEADER_NAME

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

    @property
    def module(self):
        keys = self.keys()
        if not keys:
            return None
        return self[keys[0]]


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
