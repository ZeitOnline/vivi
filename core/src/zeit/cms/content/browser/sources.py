import grokcore.component as grok
import json
import zc.sourcefactory.factories
import zeit.cms.content.sources
import zope.dottedname.resolve
import zope.interface


class API(object):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')

        try:
            name = self.request.form['name']
            source = zope.dottedname.resolve.resolve(name)
        except (KeyError, ImportError):
            raise zope.publisher.interfaces.NotFound(self.context, name)

        serialize = ISerializeSource(source().factory)
        return json.dumps(serialize())


class ISerializeSource(zope.interface.Interface):
    pass


class SerializeSource(grok.Adapter):

    grok.context(zc.sourcefactory.factories.BasicSourceFactory)
    grok.implements(ISerializeSource)

    def __init__(self, context):
        super(SerializeSource, self).__init__(context)
        self.context.isAvailable = lambda *args: True

    def __call__(self):
        return [{'id': self.getId(x), 'title': self.getTitle(x)}
                for x in self]

    def __iter__(self):
        return iter(self.context.getValues())

    def getTitle(self, value):
        return self.context.getTitle(value)

    def getId(self, value):
        return value


class SerializeContextualSource(SerializeSource):

    grok.context(zc.sourcefactory.factories.ContextualSourceFactory)

    def __iter__(self):
        return iter(self.context.getValues(None))

    def getTitle(self, value):
        return self.context.getTitle(None, value)


class SerializeObjectSource(SerializeContextualSource):

    grok.context(zeit.cms.content.sources.ObjectSource)

    def getId(self, value):
        return self.context.getToken(None, value)
