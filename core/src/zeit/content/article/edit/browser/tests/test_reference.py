import unittest

from selenium.webdriver.common.keys import Keys
import transaction
import zope.security.management

import zeit.cms.checkout.interfaces
import zeit.cms.content.sources
import zeit.cms.testing
import zeit.content.article.edit.browser.testing
import zeit.content.portraitbox.portraitbox


def add_to_clipboard(obj, name):
    principal = zope.security.management.getInteraction().participations[0].principal
    clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
    clipboard.addClip('Clip')
    clip = clipboard['Clip']
    clipboard.addContent(clip, obj, name, insert=True)
    transaction.commit()


class ImageForm(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_inline_form_saves_values(self):
        self.get_article(with_block='image')
        b = self.browser
        b.open('editable-body/blockname/@@edit-image?show_form=1')
        b.getControl('Display Mode').displayValue = ['Float']
        b.getControl('Variant Name').displayValue = ['Square 1:1']
        b.getControl('Animation').displayValue = ['Fade in']
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual(['Float'], b.getControl('Display Mode').displayValue)
        self.assertEqual(['Square 1:1'], b.getControl('Variant Name').displayValue)
        self.assertEqual(['Fade in'], b.getControl('Animation').displayValue)

    def get_image_block(self):
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        article = list(wc.values())[0]
        image_block = article.body['blockname']
        return image_block

    def test_setting_image_reference_also_sets_manual_flag(self):
        # so that the copying mechanism from IImages knows to leave the block
        # alone
        self.get_article(with_block='image')
        b = self.browser
        b.open('editable-body/blockname/@@edit-image?show_form=1')
        image_id = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        b.getControl(name='EditImage.blockname.references').value = image_id
        b.getControl('Apply').click()
        self.assertTrue(self.get_image_block().set_manually)

    def test_removing_image_reference_removes_manual_flag(self):
        self.get_article(with_block='image')
        b = self.browser
        b.open('editable-body/blockname/@@edit-image?show_form=1')
        b.getControl(name='EditImage.blockname.references').value = ''
        b.getControl('Apply').click()
        self.assertFalse(self.get_image_block().set_manually)

    def test_png_teaser_images_should_enable_colorpicker(self):
        from zeit.content.image.testing import create_image_group_with_master_image

        article = zeit.content.article.testing.create_article()
        group = create_image_group_with_master_image(
            file_name='http://xml.zeit.de/2016/DSC00109_2.PNG'
        )
        zeit.content.image.interfaces.IImages(article).image = group
        self.repository['article'] = article
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/article/@@checkout')
        b.open('@@edit.form.teaser-image?show_form=1')
        b.getControl(name='teaser-image.fill_color')

    def test_non_png_teaser_images_should_not_enable_colorpicker(self):
        from zeit.content.image.testing import create_image_group_with_master_image

        article = zeit.content.article.testing.create_article()
        group = create_image_group_with_master_image()
        zeit.content.image.interfaces.IImages(article).image = group
        self.repository['article'] = article
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/article/@@checkout')
        b.open('@@edit.form.teaser-image?show_form=1')
        with self.assertRaises(LookupError):
            b.getControl(name='teaser-image.fill_color')

    # XXX Need test for removal of color picker through removal of image
    # reference


class ImageEditTest(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_display_mode_and_variant_name_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('image')

        # Need to skip over first hidden image block (main image)
        selector_template = 'css=.block.type-image:nth-child(3) {} select'
        mode_select = selector_template.format('.fieldname-display_mode')
        variant_select = selector_template.format('.fieldname-variant_name')

        # It seems that when tabbing results in a jump that ends in a dropdown
        # menu no save is triggered and the dirty flag is not removed. Thus we
        # target a (luckily available) input field instead.
        link_input = 'css=.block.type-image:nth-child(3) input[type="text"]'

        s.waitForElementPresent(mode_select)
        self.assertEqual(['(nothing selected)', 'Large', 'Float'], s.getSelectOptions(mode_select))
        s.select(mode_select, 'label=Large')
        s.keyPress(link_input, Keys.TAB)
        s.waitForElementNotPresent('css=.field.dirty')

        s.pause(500)
        s.waitForElementPresent(variant_select)
        self.assertEqual(
            [
                '(nothing selected)',
                'Breit',
                'Original',
                'Square 1:1',
                'Templates Only',
                'Header: Von A nach B',
            ],
            s.getSelectOptions(variant_select),
        )
        s.select(variant_select, 'label=Original')
        s.keyPress(link_input, Keys.TAB)
        s.waitForElementNotPresent('css=.field.dirty')

        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(mode_select)
        s.assertSelectedLabel(mode_select, 'Large')
        s.waitForElementPresent(variant_select)
        s.assertSelectedLabel(variant_select, 'Original')

    def test_widget_shows_add_button(self):
        # this ensures that the widget can find the Article (to determine
        # ressort etc.), which means that an IReference block is adaptable to
        # ICommonMetadata.
        s = self.selenium
        self.add_article()
        # Article always has one image block already
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 1)
        s.assertElementPresent('css=.block.type-image .add_view.button')

    def add_image_to_clipboard(self):
        add_to_clipboard(self.repository['2006']['DSC00109_2.JPG'], 'my_image')
        self.add_article()
        s = self.selenium
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

    def add_group_to_clipboard(self):
        group = zeit.content.image.testing.create_image_group()
        add_to_clipboard(group, 'my_group')
        self.add_article()
        s = self.selenium
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

    def test_image_is_droppable_in_article_text(self):
        self.add_image_to_clipboard()
        s = self.selenium
        # Article always has one image block already
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 1)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_image"]', 'css=.action-article-body-content-droppable', '10,10'
        )
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 2)
        # ensure object-details are displayed
        s.waitForElementPresent('css=.block.type-image .image_details')

    def test_imagegroup_is_droppable_in_article_text(self):
        self.add_group_to_clipboard()
        s = self.selenium

        # Article always has one image block already (albeit invisible)
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 1)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_group"]', 'css=.action-article-body-content-droppable', '10,10'
        )
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 2)

    def test_changing_image_in_teaser_updates_body(self):
        self.add_group_to_clipboard()
        s = self.selenium
        landing_zone = 'css=#form-teaser-image .fieldname-image .landing-zone'
        s.waitForElementPresent(landing_zone)
        s.click('css=#edit-form-teaser .fold-link')
        s.dragAndDropToObject('//li[@uniqueid="Clip/my_group"]', landing_zone)
        s.waitForElementPresent('css=#form-teaser-image .image_details')
        s.waitForElementPresent('css=#form-article-content-main-image .image_details')

    @unittest.skip("Drag'n'drop doesn't work now.")
    def test_changing_main_image_updates_body(self):
        self.add_group_to_clipboard()
        s = self.selenium
        landing_zone = 'css=#form-article-content-main-image' ' .fieldname-main_image .landing-zone'
        s.waitForElementPresent(landing_zone)
        s.dragAndDropToObject('//li[@uniqueid="Clip/my_group"]', landing_zone)
        s.waitForElementPresent('css=#form-article-content-main-image .image_details')
        s.waitForElementPresent('css=#editable-body .image_details')

    def test_metadata_can_be_overridden_locally(self):
        self.add_image_to_clipboard()
        s = self.selenium
        # Article always has one image block already
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 1)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_image"]', 'css=.action-article-body-content-droppable', '10,10'
        )
        s.waitForCssCount('css=.block.type-image form.inline-form.wired', 2)
        # ensure object-details are displayed
        s.waitForElementPresent('css=.block.type-image .image_details')

        text = 'css=.block.type-image form.wired textarea'
        s.waitForElementPresent(text)
        s.assertValue(text, '')
        s.type(text, 'A custom caption')
        s.click('css=.block.type-image:nth-child(3)')  # Trigger blur for form.
        s.waitForElementNotPresent('css=.field.dirty')


class VideoForm(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_inline_form_saves_values(self):
        self.get_article(with_block='video')
        b = self.browser
        b.open('editable-body/blockname/@@edit-video?show_form=1')
        b.getControl('Layout').displayValue = ['large']
        b.getControl('Apply').click()
        b.reload()
        # Locate the layout widget by name here since we have several forms
        # with a "Layout" field so we couldn't be sure we have wired the
        # correct one just by looking at this one, common label.
        layout = b.getControl(name='EditVideo.blockname.layout')
        self.assertEqual(['large'], layout.displayValue)


class VideoEditTest(zeit.content.article.edit.browser.testing.EditorTestCase):
    def create_content_and_fill_clipboard(self):
        principal = zope.security.management.getInteraction().participations[0].principal
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
        clipboard.addClip('Clip')
        clip = clipboard['Clip']
        for i in range(4):
            video = zeit.content.video.video.Video()
            video.supertitle = 'MyVideo_%s' % i
            name = 'my_video_%s' % i
            self.repository[name] = video
            clipboard.addContent(clip, self.repository[name], name, insert=True)
        transaction.commit()

        s = self.selenium
        self.open('/')
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

    def setUp(self):
        super().setUp()
        self.create_content_and_fill_clipboard()

    @unittest.skip('Drag-n-drop does not work reliably with Selenium atm.')
    def test_videos_should_be_editable(self):
        s = self.selenium
        self.add_article()
        block_id = self.create_block('video', wait_for_inline=True)
        video = 'css=div[id="EditVideo.%s.video"]' % block_id

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_0"]', video)
        s.waitForElementPresent(video + ' div.supertitle:contains("MyVideo_0")')

    @unittest.skip('Drag-n-drop does not work reliably with Selenium atm.')
    def test_videos_should_be_removeable(self):
        s = self.selenium
        self.add_article()
        block_id = self.create_block('video', wait_for_inline=True)
        video = 'css=div[id="EditVideo.%s.video"]' % block_id

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_0"]', video)
        s.waitForElementPresent(video + ' div.supertitle:contains("MyVideo_0")')

        s.click(video + ' a[rel=remove]')
        s.waitForElementNotPresent(video + ' div.supertitle:contains("MyVideo_0")')

        s.dragAndDropToObject('//li[@uniqueid="Clip/my_video_0"]', video)
        s.waitForElementPresent(video + ' div.supertitle:contains("MyVideo_0")')

    def test_layout_should_be_editable(self):
        s = self.selenium
        self.add_article()
        self.create_block('video')
        select = 'css=.block.type-video form.wired select'
        s.waitForElementPresent(select)
        self.assertEqual(
            ['(nothing selected)', 'small', 'with info', 'large', 'double'],
            s.getSelectOptions(select),
        )
        s.select(select, 'label=large')
        self.eval('document.querySelector("%s").scrollIntoView()' % select.replace('css=', ''))
        s.keyPress(select, Keys.TAB)
        s.waitForElementNotPresent('css=.field.dirty')
        # Re-open the page and verify that the data is still there
        s.clickAndWait('link=Edit contents')
        s.waitForElementPresent(select)
        s.assertSelectedLabel(select, 'large')


class VolumeEditTest(zeit.content.article.edit.browser.testing.EditorTestCase):
    def add_volume_to_clipboard(self):
        from zeit.content.image.testing import create_image_group

        self.repository['imagegroup'] = create_image_group()
        volume = zeit.content.volume.volume.Volume()
        volume.year = 2006
        volume.volume = 23
        volume.product = zeit.cms.content.sources.Product('ZEI')
        volume.set_cover('portrait', 'ZEI', self.repository['imagegroup'])
        self.repository['2006']['23'] = volume
        add_to_clipboard(self.repository['2006']['23'], 'my_volume')
        self.add_article()
        s = self.selenium
        s.clickAt('//li[@uniqueid="Clip"]', '10,10')
        s.waitForElementPresent('//li[@uniqueid="Clip"][@action="collapse"]')

    def test_volume_is_droppable_in_article_text(self):
        self.add_volume_to_clipboard()
        s = self.selenium

        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/my_volume"]',
            'css=.action-article-body-content-droppable',
            '10,10',
        )
        s.waitForCssCount('css=.block.type-volume form.inline-form.wired', 1)
        # ensure object-details are displayed
        s.waitForElementPresent('css=.block.type-volume textarea ')
        s.assertTextPresent('Die Zeit, Jahrgang: 2006, Ausgabe 23')
        s.assertAttribute(
            'css=.block.type-volume img@src', '*/imagegroup/thumbnails/original/@@raw'
        )


class PortraitboxForm(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_setting_reference_clears_local_values(self):
        box = zeit.content.portraitbox.portraitbox.Portraitbox()
        box.name = 'My Name'
        self.repository['portrait'] = box
        self.get_article(with_block='portraitbox')
        b = self.browser
        b.open('editable-body/blockname/@@edit-portraitbox?show_form=1')
        b.getControl('First and last name').value = 'local'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('local', b.getControl('First and last name').value)
        b.getControl(
            name='EditPortraitbox.blockname.references'
        ).value = 'http://xml.zeit.de/portrait'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('My Name', b.getControl('First and last name').value)
