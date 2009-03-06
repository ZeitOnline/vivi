# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class Editor(zeit.cms.selenium.Test):

    def setUp(self):
        super(Editor, self).setUp()
        self.open('/repository')
        s = self.selenium
        s.selectAndWait('id=add_menu', 'label=Infobox')
        s.type('id=form.supertitle', 'Super')
        s.type('id=form.__name__', 'infobox')
        s.clickAndWait('id=form.actions.add')
        s.clickAndWait('name=form.contents.add')

    def test_enter(self):
        s = self.selenium
        s.selectFrame('id=form.contents.0..combination_01___Frame')
        s.selectFrame('index=0')
        s.fireEvent('//body', 'focus')
        s.typeKeys('//body', 'Hiya')
        s.keyPress('//body', '\\13')
        s.typeKeys('//body', 'Holla')
        s.keyPress('//body', '\\13')
        s.typeKeys('//body', 'Foobar')
        s.keyPress('//body', '\\13')

        s.selectFrame('relative=top')
