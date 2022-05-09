import zeit.cms.content.sources


class Blog:

    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url


class BlogSource(zeit.cms.content.sources.SimpleContextualXMLSource):
    product_configuration = 'zeit.content.link'
    config_url = 'source-blogs'
    default_filename = 'link-blogs.xml'

    def getValues(self, context):
        tree = self._get_tree()
        return [Blog(node.get('name'), node.get('url'))
                for node in tree.iterchildren('*')]
