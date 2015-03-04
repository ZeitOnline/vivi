import zeit.cms.testing


class SourceSecurityTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.cms.testing.ZCML_LAYER

    def setUp(self):
        super(SourceSecurityTest, self).setUp()
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/testcontent/@@checkout')
        b.getControl('Year').value = '2008'
        b.getControl('Ressort').displayValue = ['International']
        b.getControl('Title').value = 'foo'
        b.getControl(name='form.authors.0.').value = 'asdf'

    def test_product_works_with_security(self):
        b = self.browser
        b.getControl('Product id').displayValue = ['Zeit Campus']
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual(
            ['Zeit Campus'], b.getControl('Product id').displayValue)

    def test_serie_works_with_security(self):
        b = self.browser
        b.getControl('Serie').displayValue = ['Autotest']
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual(
            ['Autotest'], b.getControl('Serie').displayValue)
