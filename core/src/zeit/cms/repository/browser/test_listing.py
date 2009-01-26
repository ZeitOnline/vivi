# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import xml.sax.saxutils
import zeit.cms.selenium


class Test(zeit.cms.selenium.Test):

    def test_tablelisting_filter(self):
        s = self.selenium

        s.comment("Open a folder with articles.")
        self.open('/repository/online/2007/01')
        self.verifyTextDisplayed('Somalia')
        self.verifyTextDisplayed('presseschau')

        s.comment("type in a word to filter the table")
        s.typeKeys('name=tableFilter', 'internat')
        #s.keyUp('tableFilter', '\13')
        self.verifyTextNotDisplayed('Somalia')
        self.verifyTextDisplayed('presseschau')

    def verifyTextNotDisplayed(self, string):
        self.selenium.verifyNotVisible('//tr[contains(string(.), %s)]' %
                                       xml.sax.saxutils.quoteattr(string))

    def verifyTextDisplayed(self, string):
        self.selenium.verifyVisible('//tr[contains(string(.), %s)]' %
                                    xml.sax.saxutils.quoteattr(string))
