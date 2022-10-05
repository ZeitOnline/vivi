# coding: utf-8
import zeit.content.article.edit.browser.testing
import zeit.content.article.edit.interfaces
from unittest import mock
import zope.component

class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):

    block_type = 'videotagesschau'

    def test_hippo(self):
        import pdb; pdb.set_trace()
        self.get_article(with_empty_block=True)
        import pdb; pdb.set_trace()
        #api = zope.component.getUtility(
        #    zeit.content.article.edit.interfaces.IVideoTagesschau)
        brwsr = self.browser
        brwsr.open('editable-body/blockname/@@edit-videotagesschau?show_form=1')
        import pdb; pdb.set_trace()
        brwsr.getControl('generate-video-recommendation').click()
        brwsr.open('@@edit-citation-comment?show_form=1')  # XXX
        import pdb; pdb.set_trace()
        self.assertEqual(
            'crid://daserste.de/tagesschau24/7dd07892-7528-43f8-9a52-76679ebfc65dAAAXXX/1', brwsr.getControl('URL', index=0).value)


#####class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):
#####
#####    def test_videotagesschau_form_is_loaded(self):
#####        import pdb; pdb.set_trace()
#####        s = self.selenium
#####        self.add_article()
#####        self.create_block('videotagesschau')
#####        s.assertElementPresent('css=.block.type-videotagesschau .inline-form '
#####                               '.field.fieldname-text')
#####        s.assertElementPresent('css=.block.type-videotagesschau .inline-form '
#####                               '.field.fieldname-url '
#####                               'input[data-comments-api-url='
#####                               '"https://commentsxxxx.staging.zeit.de"]')
