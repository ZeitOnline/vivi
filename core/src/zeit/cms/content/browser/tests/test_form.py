import zeit.cms.testing


class MetadataForm(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def setUp(self):
        super().setUp()
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/testcontent/@@checkout')
        b.getLink('Edit metadata').click()

    def test_regression_emptied_subtitle_does_not_render_as_string_None(self):
        b = self.browser
        b.getControl('Year').value = '2012'
        b.getControl('Ressort').displayValue = ['International']
        b.getControl('Title').value = 'irgendwas'
        b.getControl('Subtitle').value = 'something'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        b.getControl('Subtitle').value = ''
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual('', b.getControl('Subtitle').value)

    def test_accepted_entitlements_validation(self):
        b = self.browser
        b.getControl('Accepted entitlements').value = 'irgendwas 123'
        b.getControl('Apply').click()
        self.assertEllipsis('...Invalid characters in entitlement...', b.contents)
