# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zeit.brightcove.testing
import zeit.cms.tagging.interfaces
import zeit.cms.testing
import zope.component


class KeywordTest(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.brightcove.testing.selenium_layer
    skin = 'vivi'

    def setUp(self):
        super(KeywordTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            from zeit.cms.tagging.tag import Tag
            whitelist = zope.component.getUtility(
                zeit.cms.tagging.interfaces.IWhitelist)
            whitelist['test1'] = Tag('test1')
            whitelist['test2'] = Tag('test2')
        transaction.commit()

    def test_autocomplete_and_save(self):
        self.open('/repository-brightcove/video:1234')
        s = self.selenium
        s.waitForElementPresent('css=input.autocomplete')
        s.typeKeys('css=input.autocomplete', 't')
        s.waitForVisible('css=.ui-autocomplete')
        s.assertText('css=.ui-autocomplete a', 'test1')
        #s.click('css=.ui-autocomplete a:contains(test1)')
        # down arrow
        s.keyDown('css=input.autocomplete', r'\40')
        # return
        s.keyDown('css=input.autocomplete', r'\13')
        s.waitForElementPresent('css=.objectsequencewidget li h3')
        s.assertText('css=.objectsequencewidget li h3', 'test1')
        s.click('id=form.actions.apply')
        s.waitForElementPresent('css=.objectsequencewidget li h3')
        s.assertText('css=.objectsequencewidget li h3', 'test1')
