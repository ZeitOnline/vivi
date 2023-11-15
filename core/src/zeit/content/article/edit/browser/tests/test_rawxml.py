import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_inline_form_saves_values(self):
        self.get_article(with_block='raw')
        b = self.browser
        b.open('editable-body/blockname/@@edit-rawxml?show_form=1')
        b.getControl('XML source').value = """\
<raw xmlns:ns0="http://namespaces.zeit.de/CMS/cp" ns0:__name__="blockname">
  <foo> </foo>
</raw>
"""
        b.getControl('Apply').click()
        b.reload()
        self.assertEllipsis(
            """\
<raw...xmlns:ns0="http://namespaces.zeit.de/CMS/cp"...ns0:__name__="blockname"...>
  <foo> </foo>
</raw>
""",
            b.getControl('XML source').value,
        )

    def test_xml_is_validated_root_must_be_raw_element(self):
        self.get_article(with_block='raw')
        b = self.browser
        b.open('editable-body/blockname/@@edit-rawxml?show_form=1')
        b.getControl('XML source').value = '<foo />'
        b.getControl('Apply').click()
        self.assertIn(
            '<span class="error">The root element must be &lt;raw&gt;.</span>', b.contents
        )


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_rawxml_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('raw')
        s.assertElementPresent('css=.block.type-raw .inline-form ' '.field.fieldname-xml')
