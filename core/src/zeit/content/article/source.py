import zeit.cms.content.sources


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
