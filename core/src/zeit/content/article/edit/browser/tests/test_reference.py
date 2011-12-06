# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import transaction
import unittest2
import zeit.cms.testing
import zeit.content.article.testing


class GalleryTest(unittest2.TestCase,
                  zeit.cms.testing.BrowserAssertions):

    layer = zeit.content.article.testing.TestBrowserLayer

    expected_type = 'gallery'
    attribute = 'href'

    def setUp(self):
        from zeit.content.article.interfaces import IArticle
        from zope.testbrowser.testing import Browser
        import zeit.cms.browser.form
        self.browser = browser = Browser()
        browser.addHeader('Authorization', 'Basic user:userpw')
        browser.open('http://localhost:8080/++skin++vivi/repository/online'
                     '/2007/01/Somalia/@@checkout')
        article = self.layer.setup.getRootFolder()[
            'workingcopy']['zope.user']['Somalia']
        with zeit.cms.testing.site(self.layer.setup.getRootFolder()):
            zeit.cms.browser.form.apply_default_values(article, IArticle)
        self.article_url = browser.url
        browser.open('@@contents')
        self.contents_url = browser.url
        browser.open(self.contents_url)

    def setup_content(self):
        """Create a gallery (requires folder with images)"""
        from zeit.content.gallery.browser.testing import add_folder, add_image
        browser = self.browser
        browser.open('http://localhost/++skin++cms/repository/online/2007/01')
        add_folder(browser, 'gallery')
        add_image(browser, '01.jpg')
        add_image(browser, '02.jpg')
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
        for p in article.xml.findall('//division/*'):
            p.getparent().remove(p)
        if with_empty_block:
            article.xml.body.division[self.expected_type] = ''
            article.xml.body.division[self.expected_type].set(
                '{http://namespaces.zeit.de/CMS/cp}__name__', 'blockname')
        article._p_changed = True
        transaction.commit()
        return article

    def test_no_reference_should_render(self):
        self.get_article(with_empty_block=True)
        self.browser.open('editable-body/@@contents')
        self.assert_ellipsis(
            """<...
            <div ...class="block type-%s...""" % self.expected_type)

    def test_empty_block_should_be_landing_zone(self):
        self.get_article(with_empty_block=True)
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
        self.get_article(with_empty_block=True)
        self.setup_content()
        with self.assertRaises(Exception):
            self.browser.open(
                'editable-body/blockname/@@set_reference?uniqueId='
                'http://xml.zeit.de/testcontent')
        # NOTE: the error message should be improved
        self.assert_ellipsis(
            "ConstraintNotSatisfied(<zeit.cms.repository.unknown..."
            "object at 0x...>)")

    def test_droping_type_on_landing_zone_creates_block(self):
        self.get_article()
        self.setup_content()
        self.assert_ellipsis(
            """...cms:drop-url="http://localhost:8080/++skin++vivi/workingcopy/zope.user/Somalia/editable-body/@@article-landing-zone-drop"...""")
        uuid4 = mock.Mock(side_effect=lambda: uuid4.call_count)
        with mock.patch('uuid.uuid4', new=uuid4):
            self.browser.open(
                'editable-body/@@article-landing-zone-drop?uniqueId=%s' %
                self.content_id)
        data = self.assert_json(
            {'signals': [{'args': ['1'], 'name': 'added',
                          'when': 'after-reload'},
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
            {'signals': [{'args': ['2'], 'name': 'added',
                          'when': 'after-reload'},
                         {'args': ['editable-body',
                                   'http://localhost:8080/++skin++vivi/workingcopy/zope.user/Somalia/editable-body/@@contents'],
                          'name': 'reload',
                          'when': None}]})

    def test_checkin_should_work_with_empty_block(self):
        self.get_article(with_empty_block=True)
        self.browser.open(self.article_url)
        # Assertion is that no error is raised
        self.browser.handleErrors = False
        self.browser.getLink('Checkin').click()

    def test_should_be_visible_in_read_only_mode(self):
        self.get_article(with_empty_block=True)
        self.setup_content()
        self.browser.open(
            'editable-body/blockname/@@set_reference?uniqueId=%s' %
            self.content_id)
        self.browser.open(self.article_url)
        self.browser.getLink('Checkin').click()
        self.browser.open('@@contents')
        self.assert_ellipsis(
            """<div ...class="block type-%s...""" % self.expected_type)

    def test_reference_should_be_stored_by_set_ref(self):
        article = self.get_article(with_empty_block=True)
        self.setup_content()
        self.browser.open(
            'editable-body/blockname/@@set_reference?uniqueId={0}'.format(
                self.content_id))
        self.assertEqual(
            self.content_id,
            article.xml.body.division[self.expected_type].get(self.attribute))

    def test_reference_should_be_stored_after_checkin(self):
        import zeit.cms.interfaces
        article = self.get_article(with_empty_block=True)
        self.setup_content()
        self.browser.open(
            'editable-body/blockname/@@set_reference?uniqueId={0}'.format(
                self.content_id))
        self.browser.open(self.article_url)
        self.browser.getLink('Checkin').click()
        with zeit.cms.testing.site(self.layer.setup.getRootFolder()):
            article = zeit.cms.interfaces.ICMSContent(article.uniqueId)
        self.assertEqual(
            self.content_id,
            article.xml.body.division[self.expected_type].get(self.attribute))

    def test_empty_block_should_not_provide_drop_in_readonly_mode(self):
        self.get_article(with_empty_block=True)
        self.browser.open(self.article_url)
        self.browser.getLink('Checkin').click()
        self.browser.open('@@contents')
        self.assert_ellipsis(
            '<div ...class="block type-{0}...No content referenced...'.format(
                self.expected_type))

    def test_contents_should_not_have_cache_control_header(self):
        self.get_article(with_empty_block=True)
        self.setup_content()
        self.browser.open(
            'editable-body/blockname/@@set_reference?uniqueId={0}'.format(
                self.content_id))
        self.browser.open('@@contents')
        self.assertNotIn('Cache-Control', self.browser.headers)


class InfoboxTest(GalleryTest):

    expected_type = 'infobox'

    def setup_content(self):
        from zeit.content.infobox.infobox import Infobox
        import transaction
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


class ImageTest(GalleryTest):

    expected_type = 'image'
    attribute = 'src'

    def setup_content(self):
        self.content_id = 'http://xml.zeit.de/2006/DSC00109_2.JPG'

    def test_only_specific_type_should_be_droppable(self):
        self.get_article(with_empty_block=True)
        self.setup_content()
        with self.assertRaises(Exception):
            self.browser.open(
                'editable-body/blockname/@@set_reference?uniqueId='
                'http://xml.zeit.de/testcontent')
        # NOTE: the error message should be improved
        self.assert_ellipsis("ComponentLookupError...")

    def test_empty_block_should_not_provide_drop_in_readonly_mode(self):
        # Disable inherited test because empty images are removed during
        # checkin. This will change hopefully once #8194 is implemented.
        pass


class ImageEditTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_layout_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('image')
        select = 'css=.block.type-image form.wired select'
        s.waitForElementPresent(select)
        self.assertEqual(
            ['(no value)', 'small', 'large', 'Infobox', 'Hochkant'],
            s.getSelectOptions(select))
        s.select(select, 'label=small')
        s.fireEvent(select, 'blur')
        s.waitForElementNotPresent('css=.widget-outer.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(select)
        s.assertSelectedLabel(select, 'small')

    def test_custom_caption_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('image')
        text = 'css=.block.type-image form.wired textarea'
        s.waitForElementPresent(text)
        s.assertValue(text, '')
        s.type(text, 'A custom caption')
        s.fireEvent(text, 'blur')
        s.waitForElementNotPresent('css=.widget-outer.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(text)
        s.assertValue(text, 'A custom caption')


class VideoTest(GalleryTest):

    expected_type = 'video'

    def setup_content(self):
        import zope.component
        import zeit.cms.repository.interfaces
        from zeit.content.video.video import Video
        with zeit.cms.testing.site(self.layer.setup.getRootFolder()):
            with zeit.cms.testing.interaction():
                repository = zope.component.getUtility(
                    zeit.cms.repository.interfaces.IRepository)
                repository['video'] = Video()
                repository['video_2'] = Video()
        self.content_id = repository['video'].uniqueId


class VideoEditTest(zeit.content.article.edit.browser.testing.EditorTestCase):

    def create_content_and_fill_clipboard(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction() as principal:
                clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
                clipboard.addClip('Clip')
                clip = clipboard['Clip']
                for i in range(4):
                    video = zeit.content.video.video.Video()
                    video.supertitle = u'MyVideo_%s' % i
                    name = 'my_video_%s' % i
                    self.repository[name] = video
                    clipboard.addContent(
                        clip, self.repository[name], name, insert=True)
        transaction.commit()

        s = self.selenium
        self.open('/')
        s.click('//li[@uniqueid="Clip"]')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

    def setUp(self):
        super(VideoEditTest, self).setUp()
        self.create_content_and_fill_clipboard()

    def test_videos_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('video')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_video_0"]',
            'css=div.video_1')
        s.waitForElementPresent(
            'css=div.video_1 div.supertitle:contains("MyVideo_0")')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_video_1"]',
            'css=div.video_2')
        s.waitForElementPresent(
            'css=div.video_2 div.supertitle:contains("MyVideo_1")')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_video_2"]',
            'css=div.video_1')
        s.waitForElementPresent(
            'css=div.video_1 div.supertitle:contains("MyVideo_2")')
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_video_3"]',
            'css=div.video_2')
        s.waitForElementPresent(
            'css=div.video_2 div.supertitle:contains("MyVideo_3")')

    def test_layout_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('video')
        select = 'css=.block.type-video form.wired select'
        s.waitForElementPresent(select)
        self.assertEqual(
            ['(no value)', 'small', 'with info', 'large', 'double'],
            s.getSelectOptions(select))
        s.select(select, 'label=large')
        s.fireEvent(select, 'blur')
        s.waitForElementNotPresent('css=.widget-outer.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(select)
        s.assertSelectedLabel(select, 'large')
