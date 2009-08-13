# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class AddTest(zeit.cms.selenium.Test):

    def test_adding(self):
        s = self.selenium
        self.open('/')

        s.comment('provoke validation error')
        s.select('sidebar.form.type_', 'Image Group')
        s.click('sidebar.form.actions.add')
        s.waitForElementPresent('xpath=//ul[@class="errors"]')

        s.comment('successful submit')
        s.select('sidebar.form.ressort', 'International')
        s.waitForElementPresent('xpath=//option[text() = "Meinung"]')
        s.select('sidebar.form.sub_ressort', 'Meinung')
        s.clickAndWait('sidebar.form.actions.add')
        s.verifyLocation('*/international/meinung/*-*/@@zeit.content.image.imagegroup.Add*')

        s.comment('values should be remembered in the session')
        s.verifySelectedLabel('sidebar.form.ressort', 'International')

        s.comment('but selecting something else should take preference')
        s.select('sidebar.form.type_', 'Folder')
        s.clickAndWait('sidebar.form.actions.add')
        s.verifyLocation('*/international/meinung/*-*/@@zeit.cms.repository.folder.Add*')
