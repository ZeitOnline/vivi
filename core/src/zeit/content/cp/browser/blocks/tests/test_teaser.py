# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import mock
import unittest
import zeit.cms.browser.interfaces
import zeit.cms.testing
import zeit.content.cp.browser.testing
import zeit.content.cp.centerpage
import zeit.content.cp.testing
import zope.component


class TestTeaserDisplay(unittest.TestCase):

    def setUp(self):
        from zeit.content.cp.browser.blocks.teaser import Display
        display = Display()
        display.context = mock.Mock()
        display.request = mock.Mock()
        display.layout = mock.Mock()
        display.url = mock.Mock()
        self.display = display
        self.content = mock.Mock()

    def test_get_image_should_use_preview_when_no_iimages(self):
        with mock.patch('zope.component.queryMultiAdapter') as qma:
            image = self.display.get_image(self.content)
            qma.assert_called_with((self.content, self.display.request),
                                   name='preview')
            self.display.url.assert_called_with(qma())
            self.assertEqual(image, self.display.url())

    def test_get_image_should_not_break_with_no_iimages_and_no_preview(self):
        self.assertTrue(self.display.get_image(self.content) is None)


class CommonEditTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def test_values_are_saved(self):
        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        contents_url = b.url
        b.open(
         'lead/@@landing-zone-drop?uniqueId=http://xml.zeit.de/testcontent')

        b.open(contents_url)
        b.getLink('Common').click()
        form_url = b.url

        b.getControl('Publisher', index=0).value = 'foo'
        b.getControl('Apply').click()
        b.open(form_url)
        self.assertEqual('foo', b.getControl('Publisher', index=0).value)


class TestTeaserSupertitle(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def test_no_teaser_supertitle_present_shows_supertitle_instead(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                with zeit.cms.checkout.helper.checked_out(
                    self.repository['testcontent']) as co:
                    co.supertitle = 'bar'

        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        contents_url = b.url
        b.open(
            'lead/@@landing-zone-drop?uniqueId=http://xml.zeit.de/testcontent')
        b.open(contents_url)
        self.assertEllipsis(
            '...<div class="supertitle">bar</div>...', b.contents)

    def test_if_teaser_supertitle_present_it_takes_precedence_over_supertitle(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                with zeit.cms.checkout.helper.checked_out(
                    self.repository['testcontent']) as co:
                    co.teaserSupertitle = 'foo'
                    co.supertitle = 'bar'

        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        contents_url = b.url
        b.open(
            'lead/@@landing-zone-drop?uniqueId=http://xml.zeit.de/testcontent')
        b.open(contents_url)
        self.assertEllipsis(
            '...<div class="supertitle">foo</div>...', b.contents)


class DisplayImagePositionsTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.cp.testing.layer

    def setUp(self):
        super(DisplayImagePositionsTest, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer)

    def create_teaserblock(self, layout):
        # Since the real layouts that support image positions are for the
        # parquet, we've set up the test configurations for layouts the same
        # way, but that means they only are allowed in teaser-mosaic.
        bar = zope.component.getAdapter(
            self.cp['teaser-mosaic'],
            zeit.edit.interfaces.IElementFactory, name='teaser-bar')()
        block = zope.component.getAdapter(
            bar, zeit.edit.interfaces.IElementFactory, name='teaser')()
        block.layout = zeit.content.cp.layout.get_layout(layout)
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        for i in range(3):
            article = self.repository['t%s' % i] = TestContentType()
            with zeit.cms.checkout.helper.checked_out(article) as co:
                zeit.content.image.interfaces.IImages(co).image = image
        for i in range(3):
            article = self.repository['t%s' % i]
            block.insert(0, article)
        return block

    def view(self, block):
        view = zeit.content.cp.browser.blocks.teaser.Display()
        view.context = block
        view.request = self.request
        view.update()
        return view

    def test_layout_without_image_pattern_shows_no_images(self):
        view = self.view(self.create_teaserblock(layout='short'))
        self.assertEqual(None, view.header_image)
        self.assertEqual(
            [None, None, None], [x['image'] for x in view.columns[0]])

    def test_layout_with_image_pattern_shows_header_image(self):
        # the header image is rendered above all columns, so it spans columns
        # (which is needed for multi-column layouts)
        view = self.view(self.create_teaserblock(layout='large'))
        self.assertEqual(
            'http://127.0.0.1/repository/2006/DSC00109_2.JPG/@@raw',
            view.header_image)
        self.assertEqual(
            [None, None, None], [x['image'] for x in view.columns[0]])

    def test_layout_allows_positions_shows_images_for_each_teaser(self):
        view = self.view(self.create_teaserblock(layout='parquet-regular'))
        image = 'http://127.0.0.1/repository/2006/DSC00109_2.JPG/@@raw'
        self.assertEqual(None, view.header_image)
        self.assertEqual(
            [image, image, image], [x['image'] for x in view.columns[0]])

    def test_suppressed_positions_show_now_image(self):
        block = self.create_teaserblock(layout='parquet-regular')
        block.suppress_image_positions = [1]
        view = self.view(block)
        image = 'http://127.0.0.1/repository/2006/DSC00109_2.JPG/@@raw'
        self.assertEqual(None, view.header_image)
        self.assertEqual(
            [image, None, image], [x['image'] for x in view.columns[0]])

    def test_first_position_is_not_shown_if_headerimage_present(self):
        view = self.view(self.create_teaserblock(layout='parquet-large'))
        image = 'http://127.0.0.1/repository/2006/DSC00109_2.JPG/@@raw'
        self.assertEqual(image, view.header_image)
        self.assertEqual(
            [None, image, image], [x['image'] for x in view.columns[0]])
