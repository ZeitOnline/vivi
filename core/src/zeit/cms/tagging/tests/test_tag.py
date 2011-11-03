# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zope.component
import zope.security.management
import zope.testbrowser.testing


class TestCMSContentWiring(zeit.cms.testing.FunctionalTestCase):

    # This test checks that the Tag object and its views etc are wired up
    # properly so that they can be addressed as ICMSContent and traversed to.
    # We need these things so we can use the ObjectSequenceWidget to edit tags.

    def setUp(self):
        super(TestCMSContentWiring, self).setUp()
        zope.security.management.endInteraction()
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')

    def test_object_details(self):
        from zeit.cms.tagging.tag import Tag

        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        whitelist['foo'] = Tag('foo')

        base = 'http://localhost/++skin++vivi/'
        b = self.browser
        b.open(
            base + '@@redirect_to?unique_id=tag://foo&view=@@object-details')
        self.assertEqual('<h3>foo</h3>', b.contents)
