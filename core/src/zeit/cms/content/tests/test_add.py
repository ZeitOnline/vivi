from urllib.parse import urlparse, parse_qsl
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.browser.interfaces
import zeit.cms.content.add
import zeit.cms.content.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zope.component
import zope.publisher.browser


class ContentAdderTest(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        self.request = zope.publisher.browser.TestRequest(skin=zeit.cms.browser.interfaces.ICMSSkin)

    def test_parameters_should_be_passed_in_url(self):
        adder = zeit.cms.content.add.ContentAdder(
            self.request,
            type_=zeit.cms.testcontenttype.interfaces.IExampleContentType,
            ressort='wirtschaft',
            sub_ressort='geldanlage',
            year='2009',
            month='02',
        )
        parts = urlparse(adder())
        self.assertEqual(
            '/repository/wirtschaft/geldanlage/2009-02/' '@@zeit.cms.testcontenttype.Add',
            parts.path,
        )
        query = dict(parse_qsl(parts.query))
        self.assertEqual(
            {
                'form.ressort': 'cb61e5a1d8e82f77f50ce4f86a114006',
                'form.sub_ressort': '41546881df79e17e56a3bf5ff3f447a6',
            },
            query,
        )

    def test_sub_ressort_is_optional(self):
        adder = zeit.cms.content.add.ContentAdder(
            self.request,
            type_=zeit.cms.testcontenttype.interfaces.IExampleContentType,
            ressort='wirtschaft',
            year='2009',
            month='02',
        )
        parts = urlparse(adder())
        self.assertEqual(
            '/repository/wirtschaft/2009-02/' '@@zeit.cms.testcontenttype.Add', parts.path
        )
        query = dict(parse_qsl(parts.query))
        self.assertEqual({'form.ressort': 'cb61e5a1d8e82f77f50ce4f86a114006'}, query)

    def test_ressort_and_sub_ressort_are_optional(self):
        adder = zeit.cms.content.add.ContentAdder(
            self.request,
            type_=zeit.cms.testcontenttype.interfaces.IExampleContentType,
            year='2009',
            month='02',
        )
        self.assertEqual(
            'http://127.0.0.1/repository/2009-02/' '@@zeit.cms.testcontenttype.Add?', adder()
        )

    def test_add_location_can_be_overriden_with_adapter(self):
        from zeit.cms.repository.folder import Folder

        self.repository['foo'] = Folder()

        zope.component.getSiteManager().registerAdapter(
            lambda *args: self.repository['foo'],
            (
                zeit.cms.testcontenttype.interfaces.IExampleContentType,
                zeit.cms.content.interfaces.IContentAdder,
            ),
            zeit.cms.content.interfaces.IAddLocation,
        )
        adder = zeit.cms.content.add.ContentAdder(
            self.request, type_=zeit.cms.testcontenttype.interfaces.IExampleContentType
        )
        self.assertEqual(
            'http://127.0.0.1/repository/foo/' '@@zeit.cms.testcontenttype.Add?', adder()
        )


class RessortYearFolderTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_existing_folder(self):
        from zeit.cms.repository.folder import Folder

        self.repository['wirtschaft'] = Folder()
        self.repository['wirtschaft']['2009-02'] = Folder()
        ANY = None
        adder = zeit.cms.content.add.ContentAdder(ANY, ressort='wirtschaft', year='2009', month='2')
        folder = zope.component.getMultiAdapter(
            (ExampleContentType(), adder), zeit.cms.content.interfaces.IAddLocation
        )
        self.assertEqual(self.repository['wirtschaft']['2009-02'], folder)

    def test_non_existing_folder_should_be_created(self):
        ANY = None
        adder = zeit.cms.content.add.ContentAdder(
            ANY, ressort='wirtschaft', year='2009', month='02'
        )
        folder = zope.component.getMultiAdapter(
            (ExampleContentType(), adder), zeit.cms.content.interfaces.IAddLocation
        )
        self.assertEqual(self.repository['wirtschaft']['2009-02'], folder)
