import json

import zope.app.pagetemplate
import zope.formlib.widget

import zeit.content.image.interfaces


class MDBImportWidget(zope.formlib.widget.SimpleInputWidget):
    template = zope.app.pagetemplate.ViewPageTemplateFile('mdb-widget.pt')

    def __call__(self):
        return self.template()

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        return zope.component.getUtility(zeit.content.image.interfaces.IMDB).get_body(input)

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        return value.mdb_id

    def _getFormValue(self):
        # Skip _getCurrentValueHelper() since that runs
        # `toFormValue(toFieldValue())` which is both superfluous and expensive
        # in our case.
        if self._renderedValueSet():
            return self._toFormValue(self._data)
        return self.request.form.get(self.name, self._missing)


class MDBProxy:
    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        if 'id' not in self.request.form:
            self.request.response.setStatus(400)
            return json.dumps({'message': 'GET parameter id is required'})
        mdb = zope.component.getUtility(zeit.content.image.interfaces.IMDB)
        try:
            return json.dumps(mdb.get_metadata(self.request.form['id']))
        except Exception as e:
            self.request.response.setStatus(500)
            return json.dumps({'message': 'MDB API returned ' + str(e)})
