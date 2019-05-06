from zope.cachedescriptors.property import Lazy as cachedproperty
import urllib
import zeit.content.author.interfaces
import zope.component


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
        return urllib.urlencode({
            'form.' + self.FORM_FIELDS[key]: value.encode('utf-8')
            for key, value in row.items()
            if value and key in self.FORM_FIELDS
        })
