import zeit.cms.testing


class TestProductConfigIsolation(zeit.cms.testing.ZeitCmsTestCase):
    def test_1_set_product_config(self):
        import zope.app.appsetup.product

        zope.app.appsetup.product._configs['zeit.cms']['isolated'] = 'i-am-isolated'

    def test_2_second_test_should_not_see_changes_from_first_test(self):
        import zope.app.appsetup.product

        self.assertNotIn('isolated', zope.app.appsetup.product._configs['zeit.cms'])
