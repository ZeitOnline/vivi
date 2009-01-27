# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt


import zeit.cms.selenium

class Selenium(zeit.cms.selenium.Test):

    def test_toggle_extended_search(self):
        s = self.selenium
        self.open('/')
        # Initially extended is hidden
        s.verifyVisible('id=search-extended-show')
        s.verifyNotVisible('id=search-extended-form')
        # Show extended search
        s.click('id=search-extended-show')
        s.verifyNotVisible('id=search-extended-show')
        s.verifyVisible('id=search-extended-form')
        # State is kept when the page reloads
        self.open('/')
        s.verifyNotVisible('id=search-extended-show')
        s.verifyVisible('id=search-extended-form')
        # Hide
        s.click('id=search-extended-hide')
        s.verifyVisible('id=search-extended-show')
        s.verifyNotVisible('id=search-extended-form')

    def test_extended_search_parameters_are_indicated_when_collapsed(self):
        s = self.selenium
        self.open('/')
        s.click('id=search-extended-show')
        s.type('id=search.year', '2008')
        # When we collapse the extended search there'll be an indicator:
        s.click('id=search-extended-hide')
        s.verifyText('id=search-extended-indicator', '+ Jahr: 2008')
        s.click('id=search-extended-show')
        s.select('id=search.navigation', 'label=Deutschland')
        s.click('id=search-extended-hide')
        s.verifyText(
            'id=search-extended-indicator',
            '+ Jahr: 2008 + Ressort: Deutschland')
