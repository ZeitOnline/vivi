import zeit.cms.content.sources


class Blog(object):

    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url


def unicode_or_none(value):
    if value:
        return unicode(value)


class BlogSource(zeit.cms.content.sources.SimpleContextualXMLSource):
    product_configuration = 'zeit.content.link'
    config_url = 'source-blogs'

    def getValues(self, context):
        tree = self._get_tree()
        return [Blog(unicode(node.get('name')),
                     unicode_or_none(node.get('url')))
                for node in tree.iterchildren('*')]
