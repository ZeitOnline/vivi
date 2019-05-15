from six.moves.urllib.parse import urlencode
from zeit.cms.i18n import MessageFactory as _
from zeit.content.author.author import Author
from zope.cachedescriptors.property import Lazy as cachedproperty
import gocept.form.grouped
import zeit.cms.browser.form
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


class Lookup(object):

    @cachedproperty
    def results(self):
        api = zope.component.getUtility(
            zeit.content.author.interfaces.IHonorar)
        result = api.search(self.request.form['q'])
        for row in result:
            row['form_parameters'] = self._form_parameters(row)
        return result

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
