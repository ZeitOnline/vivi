# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium
import zeit.cms.testcontenttype.interfaces
import zeit.wysiwyg.interfaces
import zope.formlib.form
import zope.interface


class WYSIWYGEdit(zeit.cms.browser.form.EditForm):
    """Edit content using wysiwyg editor."""

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.wysiwyg.interfaces.IHTMLContent))

class HTMLContent(zeit.wysiwyg.html.HTMLContentBase):
    """HTML content of an article."""

    zope.component.adapts(zeit.cms.testcontenttype.interfaces.ITestContentType)

    def get_tree(self):
        return self.context.xml['body']

class Editor(zeit.cms.selenium.Test):

    def test_enter(self):
        self.open('/repository/testcontent/@@wysiwyg.html')
        s = self.selenium
        s.selectFrame('id=form.html___Frame')
        s.selectFrame('index=0')
        s.fireEvent('//body', 'focus')
        s.typeKeys('//body', 'Hiya')
        s.keyPress('//body', '\\13')
        s.typeKeys('//body', 'Holla')
        s.keyPress('//body', '\\13')
        s.typeKeys('//body', 'Foobar')
        s.keyPress('//body', '\\13')
        s.selectFrame('relative=top')
