# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2 as unittest  # XXX
import zeit.brightcove.testing


@unittest.skip('not yet')
class TestCheckoutManager(zeit.brightcove.testing.BrightcoveTestCase):

    def get_video(self):
        import zeit.cms.interfaces
        return zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/brightcove-folder/video-1234')

    def test_can_checkout_should_be_false_on_checked_out_content(self):
        from zeit.cms.checkout.interfaces import ICheckoutManager
        manager = ICheckoutManager(self.get_video())
        self.assertTrue(manager.canCheckout)
        checked_out = manager.checkout()
        manager = ICheckoutManager(checked_out)
        self.assertFalse(manager.canCheckout)

    def test_checked_out_videos_should_not_update_brightcove(self):
        from zeit.cms.checkout.interfaces import ICheckoutManager
        import transaction
        manager = ICheckoutManager(self.get_video())
        self.assertTrue(manager.canCheckout)
        checked_out = manager.checkout()
        checked_out.title = u'Changed title'
        transaction.commit()
        self.assertEqual([], self.posts)

    def test_checked_out_videos_should_not_update_solr(self):
        from zeit.cms.checkout.interfaces import ICheckoutManager
        from zope.lifecycleevent import ObjectModifiedEvent
        import zeit.solr.interfaces
        import zope.component
        import zope.event
        manager = ICheckoutManager(self.get_video())
        self.assertTrue(manager.canCheckout)
        checked_out = manager.checkout()
        zope.event.notify(ObjectModifiedEvent(checked_out))

        solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        public_solr = zope.component.getUtility(zeit.solr.interfaces.ISolr,
                                                name='public')
        self.assertFalse(solr.update_raw.called)
        self.assertFalse(public_solr.update_raw.called)
