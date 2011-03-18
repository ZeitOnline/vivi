# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import ZODB.POSException
import cgi
import logging
import simplejson
import transaction
import zeit.cms.browser.view
import zope.app.pagetemplate
import zope.formlib.form
import zope.i18n
import zope.viewlet.viewlet


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
            message = None
            if e.args:
                if isinstance(e.args[0], basestring):
                    message = e.args[0]
                if isinstance(message, zope.i18n.Message):
                    message = zope.i18n.translate(message,
                                                  context=self.request)
            if message is None:
                message = repr(e)
            self.request.response.setStatus(500)
            self.request.response.setHeader('Content-Type', 'text/plain')
            return message
        return self.render()


def validate(context):
    validator = zeit.edit.interfaces.IValidator(context)
    if validator.status:
        css_class = 'validation-%s' % validator.status
        messages = '\n'.join(validator.messages)
        messages = cgi.escape(messages)
    else:
        css_class = ''
        messages = ''
    return (css_class, messages)


class EditBox(zope.formlib.form.SubPageEditForm):
    """Base class for an edit box."""

    template = zope.app.pagetemplate.ViewPageTemplateFile('view.editbox.pt')
    close = False
    form_fields = NotImplemented

    @property
    def form(self):
        return super(EditBox, self).template

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.close = True
        return super(EditBox, self).handle_edit_action.success(data)


class AddBox(zeit.cms.browser.form.AddFormBase,
             zope.formlib.form.AddFormBase):
    """Base class for an add box."""

    # there is no SubPageAddForm, so we set this up analog to SubPageEditForm
    zope.interface.implements(zope.formlib.interfaces.ISubPageForm)

    template = zope.app.pagetemplate.ViewPageTemplateFile('view.editbox.pt')
    close = False
    form_fields = NotImplemented

    @property
    def form(self):
        return super(AddBox, self).template

    @zope.formlib.form.action(_('Add'))
    def handle_add(self, action, data):
        self.close = True
        return super(AddBox, self).handle_add.success(data)

    def add(self):
        result = super(AddBox, self).add()
        # prevent redirect
        self._finished_add = False
        return result

    def setUpWidgets(self, ignore_request=False):
        # XXX bug in zope.formlib.form.AddFormBase: setUpWidgets does not call
        # super, thus self.adapters is not initialized, but
        # zeit.cms.browser.form.AddFormBase needs it
        self.adapters = {}
        super(AddBox, self).setUpWidgets(ignore_request)


class EditBoxAction(zope.viewlet.viewlet.ViewletBase):

    render = zope.app.pagetemplate.ViewPageTemplateFile(
        'view.editbox-action.pt')
    title = NotImplemented
    action = NotImplemented
    type = 'edit-link'
