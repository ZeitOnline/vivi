from zeit.cms.checkout.helper import checked_out
import zeit.cms.content.interfaces
import zeit.cms.testing
import zope.lifecycleevent


class ChannelCopying(zeit.cms.testing.ZeitCmsTestCase):

    def test_no_channels_copies_ressort_to_channel_on_change(self):
        with checked_out(self.repository['testcontent']) as co:
            co.ressort = u'Deutschland'
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(
                    zeit.cms.content.interfaces.ICommonMetadata, 'ressort'))
            self.assertEqual((('Deutschland', None),), co.channels)

    def test_merges_with_existing_channels(self):
        with checked_out(self.repository['testcontent']) as co:
            co.channels = (('International', None),)
            co.ressort = u'Deutschland'
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(
                    zeit.cms.content.interfaces.ICommonMetadata, 'ressort'))
            self.assertEqual((('International', None),
                              ('Deutschland', None)), co.channels)

    def test_channels_already_set_does_not_change_anything(self):
        with checked_out(self.repository['testcontent']) as co:
            co.channels = (('Deutschland', None),)
            co.ressort = u'Deutschland'
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(
                    zeit.cms.content.interfaces.ICommonMetadata, 'ressort'))
            self.assertEqual((('Deutschland', None),), co.channels)
