import zeit.cms.content.sources


class ArticleRelatedLayoutSource(zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.magazin'
    config_url = 'article-related-layout-source'
    default_filename = 'article-related-layouts.xml'
    attribute = 'id'
