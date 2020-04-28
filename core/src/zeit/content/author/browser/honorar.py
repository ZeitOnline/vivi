from six.moves.urllib.parse import urlencode
from zeit.cms.i18n import MessageFactory as _
from zeit.content.author.author import Author
from zope.cachedescriptors.property import Lazy as cachedproperty
import gocept.form.grouped
import json
import zeit.cms.browser.form
import zeit.cms.browser.view
import zeit.content.author.interfaces
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface


class ILookup(zope.interface.Interface):

    firstname = zope.schema.TextLine(title=_('Firstname'))
    lastname = zope.schema.TextLine(title=_('Lastname'))
    confirmed_duplicate = zope.schema.Bool(title=_('Add duplicate author'))


@zope.interface.implementer(zope.formlib.interfaces.IWidgetInputError)
class DuplicateAuthorWarning(Exception):

    def doc(self):
        return _(
            u'An author with the given name already exists. '
            u'If you\'d like to create another author with the same '
            u'name anyway, check "Add duplicate author" '
            u'and save the form again.')


class LookupForm(zeit.cms.browser.form.FormBase,
                 gocept.form.grouped.Form):

    form_fields = zope.formlib.form.FormFields(ILookup)
    field_groups = (gocept.form.grouped.RemainingFields(_('Create author')),)

    need_confirmation_checkbox = False

    @zope.formlib.form.action(
        _('Look up author'), condition=zope.formlib.form.haveInputWidgets)
    def handle_lookup_action(self, action, data):
        if self.ask_before_adding_author_twice(data):
            return
        self.redirect(self.url(
            self.context, '@@zeit.content.author.do_lookup') + '?' + urlencode(
                {'q': ' '.join([data['firstname'], data['lastname']])}))

    def ask_before_adding_author_twice(self, data):
        if data.get('confirmed_duplicate') or not Author.exists(
                data['firstname'], data['lastname']):
            return False
        self.need_confirmation_checkbox = True
        self.errors = (DuplicateAuthorWarning(),)
        self.status = _('There were errors')
        self.form_reset = False
        return True

    def update(self):
        super(LookupForm, self).update()
        if not self.need_confirmation_checkbox:
            self.form_fields = self.form_fields.omit('confirmed_duplicate')
            # XXX This empties the error state of other widgets, e.g.
            # "firstname required", so we only get the global error message,
            # but no error markers at the widget. How can we fix this?
            self.setUpWidgets()


class Lookup(zeit.cms.browser.view.Base):

    def __call__(self):
        func = getattr(self, self.request.method)
        return func()

    def GET(self):
        count = len(self.results)
        if count == 0:
            params = self.create_parameters
        elif count == 1:
            params = self.results[0]['form_parameters']
        else:
            params = None
        if params:
            self.redirect_to_addform(params)
            return

        # Render template to display selection
        return super(Lookup, self).__call__()

    def redirect_to_addform(self, params):
        addform = self.url(
            self.context, '@@zeit.content.author.add_contextfree')
        self.redirect(addform + '?' + params)

    def POST(self):
        if 'action-import' in self.request.form:
            params = self.result_parameters[int(
                self.request.form['selection'])]
        else:
            params = self.create_parameters
        self.redirect_to_addform(params)

    @cachedproperty
    def results(self):
        api = zope.component.getUtility(
            zeit.content.author.interfaces.IHonorar)
        result = api.search(self.request.form['q'])
        for i, row in enumerate(result):
            row['index'] = i
            row['form_parameters'] = self._form_parameters(row)
        return result

    @cachedproperty
    def result_parameters(self):
        if 'result_parameters' in self.request.form:
            return json.loads(self.request.form['result_parameters'])
        else:
            return json.dumps([x['form_parameters'] for x in self.results])

    FORM_FIELDS = {
        'gcid': 'honorar_id',
        'vorname': 'firstname',
        'nachname': 'lastname',
        'titel': 'title',
    }

    def _form_parameters(self, row):
        return urlencode({
            'form.' + self.FORM_FIELDS[key]: value.encode('utf-8')
            for key, value in row.items()
            if value and key in self.FORM_FIELDS
        })

    @cachedproperty
    def create_parameters(self):
        parts = self.request.form['q'].split(' ')
        firstname = ' '.join(parts[:-1])
        lastname = parts[-1]
        return self._form_parameters({
            'vorname': firstname, 'nachname': lastname})
