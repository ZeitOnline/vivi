# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import urllib
import zc.resourcelibrary
import zope.app.form.browser.textwidgets
import zope.component


TEMPLATE = """
<script type="text/javascript">
var fckeditor = new FCKeditor('%(field_name)s');
fckeditor.BasePath = '%(gocept_fckeditor)s/';
fckeditor.Height = 400;
fckeditor.ToolbarSet = 'Zeit';
fckeditor.Config['CustomConfigurationsPath'] = '%(zeit_wysiwyg)s/config.js';
fckeditor.Config['EditorAreaCSS'] = '%(zeit_wysiwyg)s/editor.css';
fckeditor.Config['ZeitResources'] = '%(zeit_wysiwyg)s';
fckeditor.Config['ApplicationURL'] = '%(application_url)s';

fckeditor.ReplaceTextarea();
</script>
"""


class FckEditorWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self, *args, **kw):
        zc.resourcelibrary.need('zeit.wysiwyg')

        wysiwyg_resource = zope.component.getAdapter(
            self.request, name='zeit.wysiwyg')()
        fck_resource = zope.component.getAdapter(
            self.request, name='gocept.fckeditor')()
        data = dict(
            field_name=self.name,
            gocept_fckeditor=fck_resource,
            zeit_wysiwyg=wysiwyg_resource,
            application_url=self.request.getApplicationURL()
        )
        return super(FckEditorWidget, self).__call__() + TEMPLATE % data
