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
