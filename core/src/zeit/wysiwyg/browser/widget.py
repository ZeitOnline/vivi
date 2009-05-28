# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import urllib
import zope.app.form.browser.textwidgets
import zope.component


TEMPLATE = '''\
<input type="hidden" id="%(field_name)s" name="%(field_name)s"
    value="%(html)s" />
<input type="hidden" id="%(field_name)s___Config"
    value="%(config)s" />
<iframe id="%(field_name)s___Frame" class="fckeditor"
    src="%(editor-path)s/editor/fckeditor.html?InstanceName=%(field_name)s&amp;Toolbar=Zeit"
    frameborder="0" scolling="no"></iframe>
'''


class FckEditorWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self, *args, **kw):
        wysiwyg_resource = zope.component.getAdapter(
            self.request, name='zeit.wysiwyg')()
        fck_resource = zope.component.getAdapter(
            self.request, name='gocept.fckeditor')()
        config = dict(
            EditorAreaCSS='%s/editor.css' % wysiwyg_resource,
            CustomConfigurationsPath='%s/config.js' % wysiwyg_resource,
            ZeitResources=wysiwyg_resource,
            ApplicationURL=self.request.getApplicationURL())
        data = {
            'field_name': self.name,
            'config': urllib.urlencode(config),
            'editor-path': fck_resource,
            'html': zope.app.form.browser.textwidgets.escape(
                self._getFormValue()).replace('"', '&quot;')}
        return TEMPLATE % data
