# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class AddTest(zeit.cms.selenium.Test):

    def test_adding(self):
        s = self.selenium
        self.open('/')
        s.select('form.type_', 'Image Group')
        s.select('form.ressort', 'International')
        s.waitForElementPresent('xpath=//option[text() = "Meinung"]')
        s.select('form.sub_ressort', 'Meinung')
        s.clickAndWait('form.actions.add')
        s.verifyLocation('*/international/meinung/*-*/@@zeit.content.image.imagegroup.Add')
