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
