import zeit.content.article.edit.browser.testing
import zeit.cms.testing
import zeit.content.image.testing
import zeit.arbeit.interfaces
import zope.interface


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'box'

    def test_inline_form_saves_values_for_box(self):
        article = self.get_article(with_empty_block=True)
        zope.interface.alsoProvides(article,
                                    zeit.arbeit.interfaces.IZARContent)
        b = self.browser
        b.open('editable-body/blockname/@@edit-%s?show_form=1'
               % self.block_type)
        with zeit.cms.testing.site(self.getRootFolder()):
            group = zeit.content.image.testing.create_image_group()
        b.getControl(name='form.supertitle').value = 'super'
        b.getControl(name='form.title').value = 'title'
        b.getControl(name='form.subtitle').value = 'text'
        b.getControl(name='form.image').value = group.uniqueId
        b.getControl(name='form.layout').displayValue = \
            ["Zeit Arbeit Profilbox"]
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEllipsis('text', b.getControl(name='form.subtitle').value)
        self.assertEqual('title', b.getControl(name='form.title').value)
        self.assertEqual('super', b.getControl(
            name='form.supertitle').value)
        self.assertEqual(["Zeit Arbeit Profilbox"],
                         b.getControl(name='form.layout').displayValue)
        self.assertEqual(group.uniqueId, b.getControl(name='form.image').value)

    def test_teaser_text_field_mardown_is_stored_correctly(self):
        article = self.get_article(with_empty_block=True)
        b = self.browser
        b.open('editable-body/blockname/@@edit-%s?show_form=1'
               % self.block_type)
        b.getControl(name='form.subtitle').value = '#h1 text'
        b.getControl('Apply').click()
        b.open('@@edit-%s?show_form=1' % self.block_type)
        self.assertEllipsis('h1 text\n=======', b.getControl(name="form.subtitle").value)
