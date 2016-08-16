import zeit.cms.content.sources
import zope.dottedname.resolve
import importlib


class BookRecensionCategories(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'book-recension-categories'


class GenreSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'genre-url'
    attribute = 'name'


class ArticleTemplateSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'template-source'
    attribute = 'name'
    title_xpath = '/templates/template'

    def _get_title_for(self, node):
        return unicode(node['title'])

    def allow_header_module(self, context):
        tree = self._get_tree()
        if not context.template and not context.header_layout:
            return False

        headers = tree.xpath('template[@name="{}"]/header[@name="{}"]'.format(
            context.template, context.header_layout))
        for header in headers:
            if context.header_layout == header.get('name') and header.get(
                    'allow_header_module'):
                return True
        return False

    def _provides_default(self, context, defaults):
        for default in defaults:
            if default == '*':
                continue
            try:
                iface = zope.dottedname.resolve.resolve(default)
            except ImportError:
                return False

            if iface.providedBy(context):
                return True
        return False

    def _get_default_header(self, context, template):
        for header in template.iterchildren('*'):
            if not header.get('default_for'):
                continue
            defaults = header.get('default_for').split(' ')
            if self._provides_default(context, defaults):
                return (unicode(template.get('name')),
                        unicode(header.get('name')))

    def _get_generic_default(self):
        generic_default = self._get_tree().xpath('//*[@default_for="*"]')
        if len(generic_default) == 1:
            elem = generic_default.pop()
            if elem.tag == 'header':
                return (unicode(elem.getparent().get('name')),
                        unicode(elem.get('name')))
            elif elem.tag == 'template':
                return (unicode(elem.get('name')), u'')
        return (u'', u'')

    def get_default_template(self, context):
        tree = self._get_tree()
        for template in tree.xpath('template'):
            if template.get('default_for'):
                defaults = template.get('default_for').split(' ')
                if self._provides_default(context, defaults):
                    return (unicode(template.get('name')), u'')

            # header might define default for this template
            # implicitly
            default_header = self._get_default_header(context, template)
            if default_header:
                return default_header

        return self._get_generic_default()


ARTICLE_TEMPLATE_SOURCE = ArticleTemplateSource()


class ArticleHeaderSource(zeit.cms.content.sources.MasterSlaveSource):

    product_configuration = ArticleTemplateSource.product_configuration
    config_url = ArticleTemplateSource.config_url
    attribute = 'name'
    slave_tag = 'header'
    master_node_xpath = '/templates/template'
    master_value_key = 'template'

    @property
    def master_value_iface(self):
        # prevent circular import
        import zeit.content.article.interfaces
        return zeit.content.article.interfaces.IArticleMetadata

    def _get_title_for(self, node):
        return unicode(node['title'])
