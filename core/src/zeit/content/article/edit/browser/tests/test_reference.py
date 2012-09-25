# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zeit.cms.testing
import zeit.content.article.edit.browser.testing


class ImageForm(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'image'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-image?show_form=1')
        b.getControl('Custom image sub text').value = 'foo bar'
        b.getControl('Apply').click()
        b.open('@@edit-image?show_form=1')  # XXX
        self.assertEqual(
            'foo bar', b.getControl('Custom image sub text').value)


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
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(select)
        s.assertSelectedLabel(select, 'small')

    def test_custom_caption_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('image')
        # Article always has one image block already
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 2)
        text = 'css=.block.type-image form.wired textarea'
        s.waitForElementPresent(text)
        s.assertValue(text, '')
        s.type(text, 'A custom caption')
        s.fireEvent(text, 'blur')
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(text)
        s.assertValue(text, 'A custom caption')

    def add_to_clipboard(self, obj, name):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction() as principal:
                clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
                clipboard.addClip('Clip')
                clip = clipboard['Clip']
                clipboard.addContent(clip, obj, name, insert=True)
        transaction.commit()

    def test_image_is_droppable_in_article_text(self):
        s = self.selenium
        with zeit.cms.testing.site(self.getRootFolder()):
            self.add_to_clipboard(
                self.repository['2006']['DSC00109_2.JPG'], 'my_image')
        self.add_article()
        s.click('//li[@uniqueid="Clip"]')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

        # Article always has one image block already
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 1)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_image"]', 'css=.action-content-droppable')
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 2)
        # ensure object-details are displayed
        s.waitForElementPresent('css=.block.type-image .image_details')

    def test_imagegroup_is_droppable_in_article_text(self):
        s = self.selenium
        with zeit.cms.testing.site(self.getRootFolder()):
            group = zeit.content.image.tests.create_image_group()
        self.add_to_clipboard(group, 'my_group')
        self.add_article()
        s.click('//li[@uniqueid="Clip"]')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

        # Article always has one image block already
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 1)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_group"]', 'css=.action-content-droppable')
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 2)
        # ensure object-details are displayed
        s.waitForElementPresent('css=.block.type-image .image_details')


class VideoForm(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'video'

    def test_inline_form_saves_values(self):
        self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-video?show_form=1')
        b.getControl('Layout').displayValue = ['large']
        b.getControl('Apply').click()
        # Locate the layout widget by name here since we have several forms
        # with a "Layout" field so we couldn't be sure we have wired the
        # correct one just by looking at this one, common label.
        b.open('@@edit-video?show_form=1')
        layout = b.getControl(name='EditVideo.blockname.layout')
        self.assertEqual(['large'], layout.displayValue)


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
        block_id = self.create_block('video', wait_for_inline=True)
        video = 'css=div[id="EditVideo.%s.video"]' % block_id
        video_2 = 'css=div[id="EditVideo.%s.video_2"]' % block_id

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_0"]', video)
        s.waitForElementPresent(
            video + ' div.supertitle:contains("MyVideo_0")')

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_1"]', video_2)
        s.waitForElementPresent(
            video_2 + ' div.supertitle:contains("MyVideo_1")')

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_2"]', video)
        s.waitForElementPresent(
            video + ' div.supertitle:contains("MyVideo_2")')

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_3"]', video_2)
        s.waitForElementPresent(
            video_2 + ' div.supertitle:contains("MyVideo_3")')

    def test_videos_should_be_removeable(self):
        s = self.selenium
        self.add_article()
        block_id = self.create_block('video', wait_for_inline=True)
        video = 'css=div[id="EditVideo.%s.video"]' % block_id
        video_2 = 'css=div[id="EditVideo.%s.video_2"]' % block_id

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_0"]', video)
        s.waitForElementPresent(
            video + ' div.supertitle:contains("MyVideo_0")')
        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_1"]', video_2)
        s.waitForElementPresent(
            video_2 + ' div.supertitle:contains("MyVideo_1")')

        s.click(video + ' a[rel=remove]')
        s.waitForElementNotPresent(
            video + ' div.supertitle:contains("MyVideo_0")')
        s.assertElementPresent(
            video_2 + ' div.supertitle:contains("MyVideo_1")')

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_0"]', video)
        s.waitForElementPresent(
            video + ' div.supertitle:contains("MyVideo_0")')

        s.click(video_2 + ' a[rel=remove]')
        s.waitForElementNotPresent(
            video_2 + ' div.supertitle:contains("MyVideo_1")')
        s.assertElementPresent(
            video + ' div.supertitle:contains("MyVideo_0")')

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
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(select)
        s.assertSelectedLabel(select, 'large')
