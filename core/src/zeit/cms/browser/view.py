import json
import six
import z3c.flashmessage.interfaces
import zeit.cms.application
import zope.component


class Base:

    def __call__(self):
        self.request.response.setHeader('Cache-Control', 'no-cache')
        return super(Base, self).__call__()

    def url(self, obj=None, name=None):
        # if the first argument is a string, that's the name. There should
        # be no second argument
        if isinstance(obj, six.string_types):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if name is None and obj is None:
            # create URL to view itself
            obj = self
        elif name is not None and obj is None:
            # create URL to view on context
            obj = self.context
        url = zope.component.getMultiAdapter(
            (obj, self.request), name='absolute_url')()
        if name is None:
            return url
        return '%s/%s' % (url, name)

    def redirect(self, url, status=None, trusted=False):
        assert status is None or isinstance(status, int)
        return self.request.response.redirect(
            url, status=status, trusted=trusted)

    def send_message(self, message, type='message'):
        source = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource, name='session')
        source.send(message, type)


class JSON(Base):

    resource_library = None
    template = None

    def __call__(self):
        # XXX application/json would be correct
        self.request.response.setHeader('Content-Type', 'text/json')
        result = self.json()

        # use template indicated in JSON if it's there,
        # otherwise use class template
        if isinstance(result, dict):
            template = result.pop('template', None)
            if template is None:
                template = self.template
            if template is not None:
                result['template_url'] = self.resource_url(template)
        return json.dumps(result)

    def json(self):
        return {}

    def resource_url(self, filename):
        return resource_url(self.request, self.resource_library, filename)


def resource_url(request, library, filename):
    return '/'.join([
        request.getApplicationURL(),
        zeit.cms.application.FANSTATIC_SETTINGS['publisher_signature'],
        library,
        filename,
    ])
