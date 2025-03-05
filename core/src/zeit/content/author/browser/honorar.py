from urllib.parse import urlencode
import io
import json

from zope.cachedescriptors.property import Lazy as cachedproperty
import gocept.form.grouped
import pendulum
import zope.component
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface

from zeit.cms.i18n import MessageFactory as _
from zeit.connector.search import SearchExpr
from zeit.content.author.author import HDOK_ID, TYPE, Author
from zeit.content.author.browser.interfaces import DuplicateAuthorWarning
import zeit.cms.browser.form
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.content.author.interfaces


class ILookup(zope.interface.Interface):
    firstname = zope.schema.TextLine(title=_('Firstname'))
    lastname = zope.schema.TextLine(title=_('Lastname'))
    confirmed_duplicate = zope.schema.Bool(title=_('Add duplicate author'))


class LookupForm(zeit.cms.browser.form.FormBase, gocept.form.grouped.Form):
    form_fields = zope.formlib.form.FormFields(ILookup)
    field_groups = (gocept.form.grouped.RemainingFields(_('Create author')),)

    need_confirmation_checkbox = False

    @zope.formlib.form.action(_('Look up author'), condition=zope.formlib.form.haveInputWidgets)
    def handle_lookup_action(self, action, data):
        if self.ask_before_adding_author_twice(data):
            return
        query = ' '.join([data['firstname'], data['lastname']])
        self.redirect(
            self.url(self.context, '@@zeit.content.author.do_lookup')
            + '?'
            + urlencode({'q': query.encode('utf-8')})
        )

    def ask_before_adding_author_twice(self, data):
        if data.get('confirmed_duplicate') or not Author.exists(
            data['firstname'], data['lastname']
        ):
            return False
        self.need_confirmation_checkbox = True
        self.errors = (DuplicateAuthorWarning(),)
        self.status = _('There were errors')
        self.form_reset = False
        return True

    def update(self):
        super().update()
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
        if not self.results:
            return self.redirect_to_addform(self.create_parameters)
        # Render template to display selection
        return super().__call__()

    def redirect_to_addform(self, params):
        addform = self.url(self.context, '@@zeit.content.author.add_contextfree')
        return self.redirect(addform + '?' + params)

    def POST(self):
        if 'action-import' in self.request.form:
            params = self.result_parameters[int(self.request.form['selection'])]
        else:
            params = self.create_parameters
        self.redirect_to_addform(params)

    @cachedproperty
    def results(self):
        api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
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
        'gcid': 'hdok_id',
        'vorname': 'firstname',
        'nachname': 'lastname',
        'titel': 'title',
    }
    PEN_NAMES = {
        'kuenstlervorname': 'vorname',
        'kuenstlernachname': 'nachname',
    }

    def _form_parameters(self, row):
        # Hurray special cases
        for pen, real in self.PEN_NAMES.items():
            penname = row.get(pen)
            if penname:
                row[real] = penname

        return urlencode(
            {
                'form.' + self.FORM_FIELDS[key]: str(value).encode('utf-8')
                for key, value in row.items()
                if value and key in self.FORM_FIELDS
            }
        )

    @cachedproperty
    def create_parameters(self):
        parts = self.request.form['q'].split(' ')
        firstname = ' '.join(parts[:-1])
        lastname = parts[-1]
        return self._form_parameters({'vorname': firstname, 'nachname': lastname})


class HonorarReports(zeit.cms.browser.view.Base):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        filedate = pendulum.now('UTC').strftime('%Y-%m-%d-%H-%M-%S')
        filename = f'Hdok-geloeschteGCIDs_{filedate}.csv'
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('location', 'https://www.zeit.de')
        self.request.response.setHeader(
            'Content-Disposition', 'attachment; filename="%s"' % filename
        )
        self.send_message(f'Download {filename}')
        return self.report_invalid_gcid()

    def report_invalid_gcid(self, days_ago=31):
        hdok = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        hdok_authors_deleted = hdok.invalid_gcids(days_ago)
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
        hdok_ids = [(HDOK_ID == str(x['geloeschtGCID'])) for x in hdok_authors_deleted]
        hdok_ids.extend([(HDOK_ID == str(x['refGCID'])) for x in hdok_authors_deleted])
        result = list(
            connector.search(
                [TYPE, HDOK_ID],
                (TYPE == 'author') & SearchExpr('or', *hdok_ids),
            )
        )
        content_authors = {
            x[1]: x[0].replace('http://xml.zeit.de', 'https://www.zeit.de', 1) for x in result
        }

        csv_rows = io.StringIO()
        for item in hdok_authors_deleted:
            deleted = item['geloeschtGCID']
            replaced = item['refGCID']
            if deleted not in content_authors:
                continue
            csv_rows.write(
                ';'.join(
                    [
                        str(deleted),
                        content_authors[deleted],
                        str(replaced),
                        content_authors.get(replaced, ''),
                    ]
                )
                + '\n'
            )

        csv_rows = (
            'Geloeschte HDok-ID;Vivi-Autorenobjekt zu geloeschter HDok-ID;'
            'ggf. gueltige HDok-ID;ggf. gueltiges Vivi-Autorenobjekt\n' + csv_rows.getvalue()
        )

        return csv_rows


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):
    title = _('Honorar Reports')
    viewURL = '@@HonorarReports'
    pathitem = '@@HonorarReports'
