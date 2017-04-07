from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.content.article.testing
import zope.lifecycleevent


class ChannelCopying(zeit.cms.testing.ZeitCmsTestCase):

    def test_no_channels_copies_ressort_to_channel_on_change(self):
        with checked_out(self.repository['testcontent']) as co:
            co.ressort = u'Deutschland'
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(
                    zeit.cms.testcontenttype.interfaces.IExampleContentType,
                    'ressort'))
            self.assertEqual((('Deutschland', None),), co.channels)

    def test_merges_with_existing_channels(self):
        with checked_out(self.repository['testcontent']) as co:
            co.channels = (('International', None),)
            co.ressort = u'Deutschland'
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(
                    zeit.cms.testcontenttype.interfaces.IExampleContentType,
                    'ressort'))
            self.assertEqual((('International', None),
                              ('Deutschland', None)), co.channels)

    def test_channels_already_set_does_not_change_anything(self):
        with checked_out(self.repository['testcontent']) as co:
            co.channels = (('Deutschland', None),)
            co.ressort = u'Deutschland'
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(
                    zeit.cms.testcontenttype.interfaces.IExampleContentType,
                    'ressort'))
            self.assertEqual((('Deutschland', None),), co.channels)

    def test_channels_are_not_set_if_product_forbids_it(self):
        article = ExampleContentType()
        article.product = zeit.cms.content.sources.Product(u'ZEI')
        self.repository['testcontent'] = article
        with checked_out(self.repository['testcontent']) as co:
            co.ressort = u'Deutschland'
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(
                    zeit.cms.testcontenttype.interfaces.IExampleContentType,
                    'ressort'))
            self.assertEqual((), co.channels)


class AccessChangeEvent(zeit.content.article.testing.FunctionalTestCase):

    def test_change_access_value_is_logged(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        log = zeit.objectlog.interfaces.ILog(article)
        with zeit.cms.checkout.helper.checked_out(article) as co:
            co.access = u'abo'
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(
                    zeit.cms.content.interfaces.ICommonMetadata,
                    'access'))
            entries = list(log.get_log())
            assert entries[-1].message == u'Access changed from "frei ' \
                                          u'verf\xfcgbar" to "abopflichtig"'
