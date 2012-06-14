# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import ZODB.POSException
import cgi
import json
import logging
import transaction
import zeit.cms.browser.form
import zeit.cms.browser.view
import zope.app.pagetemplate
import zope.formlib.form
import zope.i18n
import zope.viewlet.viewlet


log = logging.getLogger(__name__)


class Form(object):
    """Descriptor that extracts a variable's value from the request.

    The variable may or may not be JSON-encoded, and the request may use
    either POST or GET. It is assumed that a POSTed body is JSON-encoded as a
    whole. This means that variables may be JSON-encoded twice; it is not
    clear whether this acctually happens anywhere in the CMS, though.

    """

    def __init__(self, var_name, json=False, default=None):
        self.var_name = var_name
        self.json = json
        self.default = default

    def __get__(self, instance, class_):
        if instance is None:
            return self

        if (instance.request.method == 'POST'
            and not instance.request.form.get('_body_decoded')):
            decoded = json.loads(instance.request.bodyStream.read())
            instance.request.form.update(decoded)
            instance.request.form['_body_decoded'] = True

        value = instance.request.form.get(self.var_name, self.default)
        if value is self.default:
            return value
        if self.json and isinstance(value, basestring):
            value = json.loads(value)
        return value


class UndoableMixin(object):
    """Provides support for marking transactions undoable.

    This is supposed to be mixed into view base classes, which should call
    mark_transaction_undoable() at a convenient time in their workflow. Their
    subclasses, in turn, should set undo_description, using an i18n message.

    (This separates the what from the when, so the actual views only need to
    care about setting the appropriate description, which is all that matters
    to them.)

    Using i18n is counter-intuitive since one should usually save the base
    version and translate it upon output, but we would have to invent a format
    to store mappings, too, and that's just too complicated. We can get away
    with translating on save because these messages are seen by one user only
    (since they apply only to local content and the working copy is
    user-specific), and are expected to live for only a very short time anyway
    (until the next checkin).
    """

    # if not None this transaction will be listed in the undo history with this
    # description
    undo_description = NotImplemented

    def mark_transaction_undoable(self):
        if self.undo_description is NotImplemented:
            self.undo_description = self.__class__.__name__
        if self.undo_description:
            zeit.edit.undo.mark_transaction_undoable(zope.i18n.translate(
                self.undo_description, context=self.request))


class Action(zeit.cms.browser.view.Base, UndoableMixin):

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
        return json.dumps(dict(signals=self.signals))

    def __call__(self):
        self.signals = []
        try:
            self.update()
            self.mark_transaction_undoable()
        except ZODB.POSException.ConflictError:
            raise
        except Exception, e:
            # XXX using a view for Exception so that all AJAX/JSON request get
            # their errors handled appropriately would be nicer, but it's not
            # clear how that view would determine whether it's a json request
            # or a normal browser request.
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


class EditBox(zope.formlib.form.SubPageEditForm, UndoableMixin):
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
        self.mark_transaction_undoable()
        return super(EditBox, self).handle_edit_action.success(data)


class AddBox(zeit.cms.browser.form.AddFormBase,
             zope.formlib.form.AddFormBase,
             UndoableMixin):
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
        self.mark_transaction_undoable()
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


ViewLoader = zope.viewlet.viewlet.SimpleViewletClass('layout.view-loader.pt')
