import zope.app.appsetup.product
import zope.app.publication.interfaces
import zope.component
import zope.dottedname
import zope.i18n
import zope.security.proxy
import zope.testing.cleanup
import zeit.cms.content.source

class Blog(object):

    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url

    def __eq__(self, other):
        if not zope.security.proxy.isinstance(other, self.__class__):
            return False
        return self.name == other.name


def unicode_or_none(value):
    if value:
        return unicode(value)


class BlogSource(zeit.cms.content.source.SimpleContextualXMLSource):

    config_url = 'source-blogs'

    def getValues(self, context):
        tree = self._get_tree()
        return [Blog(unicode(node.get('name')),
                     unicode_or_none(node.get('url')))
                for node in tree.iterchildren('*')]

    def getTitle(self, context, value):
        return value.name

    def getToken(self, context, value):
        return super(BlogSource, self).getToken(context, value.name)
