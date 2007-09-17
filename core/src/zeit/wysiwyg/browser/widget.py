# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.form.browser.textwidgets


TEMPLATE = '''\
<input type="hidden" id="%(field_name)s" name="%(field_name)s"
    value="%(html)s" />
<input type="hidden" id="%(field_name)s___Config"
    value="EditorAreaCSS=%(config-path)s/editor.css&CustomConfigurationsPath=%(config-path)s/config.js" />
<iframe id="%(field_name)s___Frame" class="fckeditor"
    src="%(editor-path)s/editor/fckeditor.html?InstanceName=%(field_name)s&amp;Toolbar=Zeit"
    frameborder="0" scolling="no"></iframe>
'''


class FckEditorWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self, *args, **kw):
        data = {
            'field_name': self.name,
            'config-path': '/@@/zeit.wysiwyg',
            'editor-path': '/@@/gocept.fckeditor',
            'html': zope.app.form.browser.textwidgets.escape(
                self._getFormValue()).replace('"', '&quot;')}
        return TEMPLATE % data
