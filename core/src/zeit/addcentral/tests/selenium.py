# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class AddTest(zeit.cms.selenium.Test):

    def test_adding(self):
        s = self.selenium
        self.open('/')
        s.select('sidebar.form.type_', 'Image Group')
        s.select('sidebar.form.ressort', 'International')
        s.waitForElementPresent('xpath=//option[text() = "Meinung"]')
        s.select('sidebar.form.sub_ressort', 'Meinung')
        s.clickAndWait('sidebar.form.actions.add')
        s.verifyLocation('*/international/meinung/*-*/@@zeit.content.image.imagegroup.Add*')

        s.verifySelectedLabel('sidebar.form.ressort', 'International')
