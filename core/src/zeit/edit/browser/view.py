# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import ZODB.POSException
import simplejson
import logging
import transaction
import zeit.cms.browser.view
import zope.i18n


log = logging.getLogger(__name__)


class Form(object):

    def __init__(self, var_name, json=False, default=None):
        self.var_name = var_name
        self.json = json
        self.default = default

    def __get__(self, instance, class_):
        if instance is None:
            return self

        if (instance.request.method == 'POST'
            and not instance.request.form.get('_body_decoded')):
            decoded = simplejson.loads(instance.request.bodyStream.read())
            instance.request.form.update(decoded)
            instance.request.form['_body_decoded'] = True

        value = instance.request.form.get(self.var_name, self.default)
        if value is self.default:
            return value
        if self.json and isinstance(value, basestring):
            value = simplejson.loads(value)
        return value


class Action(zeit.cms.browser.view.Base):

    def signal_context_reload(self):
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))

    def signal(self, when, name, *args):
        self.signals.append(dict(
            args=args,
            name=name,
            when=when,
        ))

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/json')
        return simplejson.dumps(dict(signals=self.signals))

    def __call__(self):
        self.signals = []
        try:
            self.update()
        except ZODB.POSException.ConflictError:
            raise
        except Exception, e:
            log.warning('Error in action', exc_info=True)
            transaction.doom()
            message = e.args[0]
            if isinstance(message, zope.i18n.Message):
                message = zope.i18n.translate(message, context=self.request)
            self.request.response.setStatus(500)
            self.request.response.setHeader('Content-Type', 'text/plain')
            return message
        return self.render()

