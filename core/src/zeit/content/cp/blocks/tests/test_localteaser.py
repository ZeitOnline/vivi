import zope.interface

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.content.cp.blocks.localteaser import ITeaserOverrides
import zeit.content.cp.testing


class IExample(zope.interface.Interface):
    pass


class ISpecialContent(zeit.cms.testcontenttype.interfaces.IExampleContentType):
    pass


def default_example(context):
    return 'default'


def special_example(context):
    return 'special'


def override_example(context):
    return 'override'


class LocalTeaserTest(zeit.content.cp.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        cp = self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.module = cp.body['lead'].create_item('local-teaser')

    def test_local_teaser_also_provides_content_interfaces(self):
        self.module.append(self.repository['testcontent'])
        content = list(self.module)[0]
        self.assertIn(ICommonMetadata, list(zope.interface.providedBy(content)))

    def test_override_interface_is_more_specific_than_content_interfaces(self):
        zca = zope.component.getSiteManager()
        zca.registerAdapter(default_example, (ICommonMetadata,), IExample)
        zca.registerAdapter(special_example, (ISpecialContent,), IExample)
        zca.registerAdapter(override_example, (ITeaserOverrides,), IExample)

        self.assertEqual('default', IExample(self.repository['testcontent']))
        with checked_out(self.repository['testcontent']) as co:
            zope.interface.alsoProvides(co, ISpecialContent)
        self.assertEqual('special', IExample(self.repository['testcontent']))

        self.module.append(self.repository['testcontent'])
        content = list(self.module)[0]
        self.assertEqual('override', IExample(content))
