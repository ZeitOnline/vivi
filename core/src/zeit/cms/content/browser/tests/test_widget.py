import zeit.cms.testing


class TestXMLSnippetRendersErrorsOnWidget(zeit.cms.testing.BrowserTestCase):

    def test_error_is_displayed_on_widget(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++cms/repository/testcontent/@@checkout')
        b.getLink('Edit metadata').click()
        b.getControl('Title').value = ('This text is longer than 70 '
                                       'characters, which is the current max '
                                       'length for the title in the metadata '
                                       'form.')
        b.getControl('Apply').click()
        self.assert_ellipsis("""...
        <div class="error">
          <span class="error">Value is too long</span>
        </div>
        <div class="widget"><textarea cols="60" id="form.title"...""",
                             b.contents)
