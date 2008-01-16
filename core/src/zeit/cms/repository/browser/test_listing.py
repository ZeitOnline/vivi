# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.selenium.pytest


class Test(zc.selenium.pytest.Test):

    def test_tablelisting_filter(self):
        s = self.selenium

        s.comment("Open a folder with articles.")
        s.open('http://%s/++skin++cms/repository/online/2007/01' %(s.server, ))
        self.assertTextDisplayed('Bomben in Bangkok')

        s.comment("type in a word to filter the table")
        s.type('tableFilter', 'internat')
        s.keyUp('tableFilter', '\13')
        self.assertTextDisplayed('Dialog abgebrochen')
        
        self.assertTextNotDisplayed('Der letzte Star springt ab')

        s.comment('Now test if it filter correctly for issue.')
        s.type('tableFilter', '47')
        s.keyUp('tableFilter', '\13')
        self.assertTextDisplayed('Der Tod des Diktators')

    def test_deleteFile(self):
        s = self.selenium
        
        s.comment("Open a folder with articles.")
        s.open('http://%s/++skin++cms/repository/online/2007/01' %(s.server, ))

        s.comment("Select one file.")
        self.assertTextDisplayed('Bomben in Bangkok')
        s.click('//tr[@deleteid = "thailand-anschlaege"]')
        s.click('//input[@type="submit"]')
        self.assertTextNotDisplayed('Positive Entwicklung')


    def assertTextNotDisplayed(self, string):
        s = self.selenium
        expr = '//td[text() = "%s"]/..[contains(@style, "display: none")]' %string
        s.assertElementPresent(expr)

    def assertTextDisplayed(self, string):
        s = self.selenium
        expr = ('//td[text() = "%s"]/..[not(contains(@style, "display: none"))]'
                %string)
        s.assertElementPresent(expr)
