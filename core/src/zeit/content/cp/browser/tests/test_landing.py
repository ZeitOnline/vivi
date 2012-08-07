# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.checkout.helper
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.content.cp.browser.testing
import zeit.content.cp.centerpage
import zeit.content.cp.testing
import zope.component
import zope.publisher.browser


class RelatedTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(RelatedTest, self).setUp()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        c1 = repository['c1'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        c2 = repository['c2'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        with zeit.cms.checkout.helper.checked_out(
            content) as co:
            relateds = zeit.cms.related.interfaces.IRelatedContent(co)
            relateds.related = (c1, c2)
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSSkin)

    def test_created_relateds(self):
        self.request.form['uniqueId'] = 'http://xml.zeit.de/testcontent'
        view = zope.component.getMultiAdapter(
            (self.cp['lead'], self.request), name='landing-zone-drop')
        view()
        self.assertEquals(1, len(self.cp['lead'].values()))
        block = self.cp['lead'].values()[0]
        self.assertEquals(
            [u'http://xml.zeit.de/testcontent',
             u'http://xml.zeit.de/c1',
             u'http://xml.zeit.de/c2'],
            [x.uniqueId for x in block])

    def test_no_relateds(self):
        self.request.form['uniqueId'] = 'http://xml.zeit.de/testcontent'
        self.request.form['relateds'] = 'false'
        view = zope.component.getMultiAdapter(
            (self.cp['lead'], self.request), name='landing-zone-drop')
        view()
        self.assertEquals(1, len(self.cp['lead'].values()))
        block = self.cp['lead'].values()[0]
        self.assertEquals(
            [u'http://xml.zeit.de/testcontent'],
            [x.uniqueId for x in block])
