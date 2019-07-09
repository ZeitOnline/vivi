import json
import zeit.content.image.interfaces
import zope.formlib.widget


class MDBImportWidget(zope.formlib.widget.SimpleInputWidget):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'mdb-widget.pt')

    def __call__(self):
        return self.template()

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        # XXX return zope.component.getUtility(IMDB).get_body(input)
        return None

    def _toFormValue(self, value):
        # We only work in an AddForm, i.e. one-way.
        return self._missing


class MDBProxy(object):

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
