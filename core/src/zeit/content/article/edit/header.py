import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.field
import zeit.content.article.edit.container
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.article.source
import zope.component


HEADER_NAME = 'editable-header'


@grok.implementer(zeit.content.article.edit.interfaces.IHeaderArea)
class HeaderArea(zeit.content.article.edit.container.TypeOnTagContainer, grok.MultiAdapter):
    grok.provides(zeit.content.article.edit.interfaces.IHeaderArea)
    grok.adapts(zeit.content.article.interfaces.IArticle, gocept.lxml.interfaces.IObjectified)

    __name__ = HEADER_NAME

    def insert(self, position, item):
        self.clear()
        return super().insert(position, item)

    def add(self, item):
        self.clear()
        return super().add(item)

    def clear(self):
        for key in list(self.keys()):
            self._delete(key)

    def _get_keys(self, xml_node):
        result = []
        for child in xml_node.iterchildren('*'):
            result.append(self._set_default_key(child))
        return result

    def values(self):
        # We re-implement values() so it works without keys(), since those are
        # not present in the repository.
        result = []
        for child in self.xml.iterchildren('*'):
            element = self._get_element_for_node(child)
            if element is None:
                element = self._get_element_for_node(child, zeit.edit.block.UnknownBlock.type)
            result.append(element)
        return result

    @property
    def module(self):
        values = self.values()
        if values:
            return values[0]
        # XXX Kludgy emulation of things that should be in the header, but
        # aren't yet.
        body = zeit.content.article.edit.interfaces.IEditableBody(self.__parent__)
        try:
            block = body[0]
        except KeyError:
            return None
        if (
            zeit.content.article.edit.interfaces.IVideo.providedBy(block)
            and 'header' in (block.layout or '')
        ) or (
            zeit.content.article.edit.interfaces.IImage.providedBy(block)
            and block.display_mode != 'float'
        ):
            return block
        return None


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.content.article.edit.interfaces.IHeaderArea)
def get_header_area(article):
    node = article.xml.xpath('//head/header')
    if not node:
        # XXX locate the XML object into the workingcopy so that edit
        # permissions can be found (which makes this security declaration
        # somewhat unhelpful since it doesn't work without additional setup).
        head = article.xml['head']
        head = zeit.cms.content.field.located(head, article, 'header')
        head.append(lxml.objectify.E.header())
    node = article.xml.xpath('//head/header')[0]
    return zope.component.queryMultiAdapter(
        (article, zope.security.proxy.removeSecurityProxy(node)),
        zeit.content.article.edit.interfaces.IHeaderArea,
    )


class ModuleSource(zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.article'
    config_url = 'header-module-source'
    default_filename = 'article-header-modules.xml'
    attribute = 'id'

    # For consistency with the zeit.content.cp config files.
    def _get_title_for(self, node):
        return node.get('title')


MODULES = ModuleSource()


@grok.subscribe(zeit.content.article.interfaces.IArticle, zope.lifecycleevent.IObjectModifiedEvent)
def clear_header_module_if_not_allowed_by_template(context, event):
    IArticle = zeit.content.article.interfaces.IArticle
    for description in event.descriptions:
        if description.interface is IArticle and (
            'template' in description.attributes or 'header_layout' in description.attributes
        ):
            break
    else:
        return

    source = zeit.content.article.source.ARTICLE_TEMPLATE_SOURCE.factory
    if not source.allow_header_module(context):
        context.header.clear()
