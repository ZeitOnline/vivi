# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.cms.testing
import zeit.content.article.testing


class GalleryTest(unittest2.TestCase,
                  zeit.cms.testing.BrowserAssertions):

    layer = zeit.content.article.testing.TestBrowserLayer

    expected_type = 'gallery'

    def setUp(self):
        from zope.testbrowser.testing import Browser
        self.browser = browser = Browser()
        browser.addHeader('Authorization', 'Basic user:userpw')
        browser.open('http://localhost:8080/++skin++vivi/repository/online'
                     '/2007/01/Somalia/@@checkout')
        browser.open('@@contents')
        self.contents_url = browser.url
        browser.open(self.contents_url)

    def setup_content(self):
        """Create a gallery (requires folder with images)"""
        from zeit.content.gallery.browser.testing import add_folder, add_image
        browser = self.browser
        browser.open('http://localhost/++skin++cms/repository/online/2007/01')
        _ = add_folder(browser, 'gallery')
        _ = add_image(browser, '01.jpg')
        _ = add_image(browser, '02.jpg')
        browser.getLink('01').click()
        menu = browser.getControl(name='add_menu')
        menu.displayValue = ['Gallery']
        browser.open(menu.value[0])
        browser.getControl('File name').value = 'island'
        browser.getControl('Title').value = 'Auf den Spuren der Elfen'
        browser.getControl('Ressort').displayValue = ['Reisen']
        browser.getControl(name="form.image_folder").value = (
            'http://xml.zeit.de/online/2007/01/gallery')
        browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
        browser.getControl(name="form.actions.add").click()
        browser.getLink('Checkin').click()
        self.content_id = 'http://xml.zeit.de/online/2007/01/island'
        browser.open(self.contents_url)

    def get_article(self, with_empty_block=False):
        import transaction
        article = self.layer.setup.getRootFolder()[
            'workingcopy']['zope.user']['Somalia']
        for p in article.xml.body.division.getchildren():
            article.xml.body.division.remove(p)
        if with_empty_block:
            article.xml.body.division[self.expected_type] = ''
            article.xml.body.division[self.expected_type].set(
                '{http://namespaces.zeit.de/CMS/cp}__name__', 'blockname')
        article._p_changed = True
        transaction.commit()
        return article

    def test_no_reference_should_render(self):
        article = self.get_article(with_empty_block=True)
        self.browser.open('editable-body/@@contents')
        self.assert_ellipsis(
            """<...
            <div ...class="block type-%s...""" % self.expected_type)

    def test_empty_block_should_be_landing_zone(self):
        article = self.get_article(with_empty_block=True)
        self.setup_content()
        self.browser.open(
            'editable-body/blockname/@@set_reference?uniqueId=%s' %
            self.content_id)
        self.assert_json(
            {'signals': [{'args': [
                'blockname',
                'http://localhost:8080/++skin++vivi/workingcopy/zope.user/Somalia/editable-body/blockname/@@contents'],
                'name': 'reload',
                'when': None}]})
        self.browser.open('@@contents')
        self.assert_ellipsis(
            """<div ...class="block type-%s...""" % self.expected_type)

    def test_only_specific_type_should_be_droppable(self):
        article = self.get_article(with_empty_block=True)
        self.setup_content()
        with self.assertRaises(Exception):
            self.browser.open(
                'editable-body/blockname/@@set_reference?uniqueId='
                'http://xml.zeit.de/testcontent')
        # NOTE: the error message should be improved
        self.assert_ellipsis(
            "ConstraintNotSatisfied(<zeit.cms.repository.unknown."
            "PersistentUnknownResource object at 0x...>)")

    def test_droping_type_on_landing_zone_creates_block(self):
        article = self.get_article()
        self.setup_content()
        self.assert_ellipsis(
            """...cms:drop-url="http://localhost:8080/++skin++vivi/workingcopy/zope.user/Somalia/editable-body/@@article-landing-zone-drop"...""")
        uuid4 = mock.Mock(side_effect=lambda: uuid4.call_count)
        with mock.patch('uuid.uuid4', new=uuid4):
            self.browser.open(
                'editable-body/@@article-landing-zone-drop?uniqueId=%s' %
                self.content_id)
        data = self.assert_json(
            {'signals': [{'args': ['1'], 'name': 'added', 'when': 'after-reload'},
                         {'args': ['editable-body',
                                   'http://localhost:8080/++skin++vivi/workingcopy/zope.user/Somalia/editable-body/@@contents'],
                          'name': 'reload',
                          'when': None}]})
        self.browser.open(self.contents_url)
        self.assert_ellipsis(
            """<...
                <div ...class="block type-%s...""" % self.expected_type)
        # Each block has its own landing zone:
        id = data['signals'][0]['args'][0]
        with mock.patch('uuid.uuid4', new=uuid4):
            self.browser.open(
                'editable-body/%s/@@article-landing-zone-drop?uniqueId=%s' % (
                    id, self.content_id))
        self.assert_json(
            {'signals': [{'args': ['2'], 'name': 'added', 'when': 'after-reload'},
                         {'args': ['editable-body',
                                   'http://localhost:8080/++skin++vivi/workingcopy/zope.user/Somalia/editable-body/@@contents'],
                          'name': 'reload',
                          'when': None}]})


class InfoboxTest(GalleryTest):

    expected_type = 'infobox'

    def setup_content(self):
        from zeit.content.infobox.infobox import Infobox
        import transaction
        import zeit.cms.testing
        ib = Infobox()
        ib.supertitle = u'infobox title'
        root = self.layer.setup.getRootFolder()
        with zeit.cms.testing.site(root):
            root['repository']['infobox'] = ib
        self.content_id = 'http://xml.zeit.de/infobox'
        transaction.commit()


class PortraitboxTest(GalleryTest):

    expected_type = 'portraitbox'

    def setup_content(self):
        from zeit.content.portraitbox.portraitbox import Portraitbox
        import transaction
        import zeit.cms.testing
        pb = Portraitbox()
        root = self.layer.setup.getRootFolder()
        with zeit.cms.testing.site(root):
            with zeit.cms.testing.interaction():
                root['repository']['pb'] = pb
        self.content_id = 'http://xml.zeit.de/pb'
        transaction.commit()

    def test_layout_should_be_editable(self):
        self.setup_content()
        article = self.get_article(with_empty_block=True)
        article.xml.body.division[self.expected_type].set(
            'href', self.content_id)
        article._p_changed = True
        self.browser.open(self.contents_url)
        self.browser.getLink('Edit').click()
        self.assertEqual(
            ['(no value)', 'short', 'wide'],
            self.browser.getControl('Layout').displayOptions)
        self.browser.getControl('Layout').displayValue = ['wide']
        self.browser.getControl('Apply').click()
        self.assert_ellipsis("<...self.close()...")
        # The layout is used as a css-class:
        self.browser.open(self.contents_url)
        self.assert_ellipsis(
            """...<div ...class="wide ...""")


class ImageTest(GalleryTest):

    expected_type = 'image'

    def setup_content(self):
        self.content_id = 'http://xml.zeit.de/2006/DSC00109_2.JPG'

    def test_only_specific_type_should_be_droppable(self):
        article = self.get_article(with_empty_block=True)
        self.setup_content()
        with self.assertRaises(Exception):
            self.browser.open(
                'editable-body/blockname/@@set_reference?uniqueId='
                'http://xml.zeit.de/testcontent')
        # NOTE: the error message should be improved
        self.assert_ellipsis("ComponentLookupError...")

    def test_layout_should_be_editable(self):
        article = self.get_article(with_empty_block=True)
        self.browser.open(self.contents_url)
        self.browser.getLink('Edit').click()
        self.assertEqual(
            ['(no value)', 'small', 'large', 'Infobox', 'Hochkant'],
            self.browser.getControl('Layout').displayOptions)
        self.browser.getControl('Layout').displayValue = ['large']
        self.browser.getControl('Apply').click()
        self.assert_ellipsis("<...self.close()...")
        # The layout is used as a css-class:
        self.browser.open(self.contents_url)
        self.assert_ellipsis(
            """...<div ...class="large ...""")


class VideoTest(GalleryTest):

    layer = zeit.content.article.testing.ArticleBrightcoveLayer
    expected_type = 'video'

    def setup_content(self):
        self.content_id = 'http://video.zeit.de/video/1234'

    def test_layout_should_be_editable(self):
        article = self.get_article(with_empty_block=True)
        self.browser.open(self.contents_url)
        self.browser.getLink('Edit').click()
        self.assertEqual(
            ['(no value)', 'small', 'with info', 'large', 'double'],
            self.browser.getControl('Layout').displayOptions)
        self.browser.getControl('Layout').displayValue = ['large']
        self.browser.getControl('Apply').click()
        self.assert_ellipsis("<...self.close()...")
        # The layout is used as a css-class:
        self.browser.open(self.contents_url)
        self.assert_ellipsis(
            """...<div ...class="large ...""")

    def test_two_videos_should_be_editable(self):
        article = self.get_article(with_empty_block=True)
        self.browser.open(self.contents_url)
        self.browser.getLink('Edit').click()
        self.browser.getControl('Video', index=0).value = (
            'http://video.zeit.de/video/1234')
        self.browser.getControl('Video 2').value = (
            'http://video.zeit.de/video/6789')
        self.browser.getControl('Apply').click()
        self.assert_ellipsis("<...self.close()...")
        self.browser.open(self.contents_url)
        self.assert_ellipsis(
            """<...
               <div class="video-image video_1">
                  <img src="http://videostillurl" />
               </div>
               <div class="video-image video_2">
                  <img src="http://videostillurl" />
               </div>
            ...""")
