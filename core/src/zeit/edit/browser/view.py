from zeit.cms.i18n import MessageFactory as _
import html
import json
import logging
import importlib.resources
import xml.sax.saxutils
import zeit.cms.browser.form
import zeit.cms.browser.view
import zope.browserpage
import zope.formlib.form
import zope.i18n
import zope.viewlet.manager
import zope.viewlet.viewlet


log = logging.getLogger(__name__)


class Form:
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

        if (instance.request.method == 'POST' and
                not instance.request.form.get('_body_decoded')):
            decoded = json.loads(instance.request.bodyStream.read(
                int(instance.request['CONTENT_LENGTH'])))
            instance.request.form.update(decoded)
            instance.request.form['_body_decoded'] = True

        value = instance.request.form.get(self.var_name, self.default)
        if value is self.default:
            return value
        if self.json and isinstance(value, str):
            value = json.loads(value)
        return value


class UndoableMixin:
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

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.signals = []
        self.data = {}

    def reload(self, element=None):
        if element is None:
            element = self.context
        self.signal(
            None, 'reload', element.__name__, self.url(element, '@@contents'))

    def signal(self, when, name, *args):
        signal = dict(args=args, name=name, when=when)
        # Guard to avoid duplicate signals, e.g. reloading the container twice
        if signal not in self.signals:
            self.signals.append(signal)

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/json')
        return json.dumps(dict(signals=self.signals, data=self.data))

    def __call__(self):
        self.update()
        self.mark_transaction_undoable()
        return self.render()


def validate(context):
    validator = zeit.edit.interfaces.IValidator(context)
    if validator.status:
        css_class = 'validation-%s' % validator.status
        messages = '\n'.join(validator.messages)
        messages = html.escape(messages)
    else:
        css_class = ''
        messages = ''
    return (css_class, messages)


class EditBox(zeit.cms.browser.form.WidgetCSSMixin,
              zope.formlib.form.SubPageEditForm,
              UndoableMixin):
    """Base class for an edit box."""

    template = zope.browserpage.ViewPageTemplateFile('view.editbox.pt')
    form = zope.app.pagetemplate.ViewPageTemplateFile(
        'subpageform.pt', str(importlib.resources.files('zeit.cms.browser')))
    close = False
    form_fields = NotImplemented

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.close = True
        self.mark_transaction_undoable()
        return super().handle_edit_action.success(data)


# There is no SubPageAddForm, so we set this up analog to SubPageEditForm
@zope.interface.implementer(zope.formlib.interfaces.ISubPageForm)
class AddBox(zeit.cms.browser.form.AddFormBase,
             zope.formlib.form.AddFormBase,
             UndoableMixin):
    """Base class for an add box."""

    template = zope.browserpage.ViewPageTemplateFile('view.editbox.pt')
    close = False
    form_fields = NotImplemented

    @property
    def form(self):
        return super().template

    @zope.formlib.form.action(_('Add'))
    def handle_add(self, action, data):
        self.close = True
        self.mark_transaction_undoable()
        return super().handle_add.success(data)

    def add(self):
        result = super().add()
        # prevent redirect
        self._finished_add = False
        return result

    def setUpWidgets(self, ignore_request=False):
        # XXX bug in zope.formlib.form.AddFormBase: setUpWidgets does not call
        # super, thus self.adapters is not initialized, but
        # zeit.cms.browser.form.AddFormBase needs it
        self.adapters = {}
        super().setUpWidgets(ignore_request)


class EditBoxAction(zope.viewlet.viewlet.ViewletBase):

    render = zope.browserpage.ViewPageTemplateFile(
        'view.editbox-action.pt')
    title = NotImplemented
    action = NotImplemented
    type = 'edit-link'


ViewLoader = zope.viewlet.viewlet.SimpleViewletClass('layout.view-loader.pt')


class ErrorPreventingViewletManager(
        zope.viewlet.manager.WeightOrderedViewletManager):
    """Prevents rendering viewlets which raise an Exception in render."""

    wrapper = '<div class="error">{error_msg}</div>'

    def render_viewlet(self, viewlet):
        "Renders viewlet. Returns error message if viewlet cannot be rendered."
        try:
            return viewlet.render()
        except Exception as e:
            mapping = dict(name=viewlet.__name__, exc_type=type(e).__name__,
                           exc_msg=str(e))
            error_msg = _(
                "There was an error rendering ${name}: ${exc_type} ${exc_msg}",
                mapping=mapping)
            log.warning('There was an error rendering %s at %s' % (
                mapping['name'], self.request.getURL()), exc_info=True)
            return self.wrapper.format(
                error_msg=xml.sax.saxutils.escape(zope.i18n.translate(
                    error_msg, context=self.request)))
