import gocept.fckeditor.resources
import zeit.cms.browser.view
import zope.app.form.browser.textwidgets


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
        gocept.fckeditor.resources.fckeditor.need()
        data = {
            'field_name': self.name,
            'gocept_fckeditor': zeit.cms.browser.view.resource_url(
                self.request, 'gocept.fckeditor', ''
            ),
            # Need a Zope resource so it evaluates TAL
            # (to need() more resources)
            'zeit_wysiwyg': zope.component.getAdapter(self.request, name='zeit.wysiwyg')(),
            'application_url': self.request.getApplicationURL(),
        }
        return super().__call__() + TEMPLATE % data
