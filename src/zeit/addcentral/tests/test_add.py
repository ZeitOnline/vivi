# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.addcentral.testing
import zeit.cms.testing


class JavascriptTest(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.addcentral.testing.selenium_layer
    skin = 'vivi'

    def test_adding(self):
        s = self.selenium
        self.open('/')

        # provoke validation error
        s.waitForElementPresent('sidebar.form.type_')
        s.click('sidebar.form.actions.add')
        s.waitForElementPresent('xpath=//ul[@class="errors"]')

        # successful submit
        s.select('sidebar.form.type_', 'Image Group')
        s.select('sidebar.form.ressort', 'International')
        s.waitForElementPresent('xpath=//option[text() = "Meinung"]')
        s.select('sidebar.form.sub_ressort', 'Meinung')
        s.click('sidebar.form.actions.add')
        s.waitForLocation(
            '*/international/meinung/*-*/@@zeit.content.image.imagegroup.Add*')

        # values should be remembered in the session
        s.waitForElementPresent('sidebar.form.ressort')
        s.assertSelectedLabel('sidebar.form.ressort', 'International')

        # but selecting something else should take preference
        s.select('sidebar.form.type_', 'Folder')
        s.click('sidebar.form.actions.add')
        s.waitForLocation(
            '*/international/meinung/*-*/@@zeit.cms.repository.folder.Add*')
