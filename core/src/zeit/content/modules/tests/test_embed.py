import lxml.objectify
import mock
import zeit.content.modules.embed
import zeit.content.modules.testing


class ConsentInfo(zeit.content.modules.testing.FunctionalTestCase):

    def setUp(self):
        super(ConsentInfo, self).setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.embed.Embed(
            self.context, lxml.objectify.XML('<container/>'))
        self.module.url = 'https://twitter.com/example'

    def test_stores_local_values_in_xml(self):
        info = zeit.cmp.interfaces.IConsentInfo(self.module)
        self.assertEqual(True, info.has_thirdparty)
        self.assertEqual(('twitter',), info.thirdparty_vendors)
