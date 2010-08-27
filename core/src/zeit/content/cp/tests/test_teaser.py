# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.testing
import zeit.content.cp.testing


class XMLTeaserBase(zeit.content.cp.testing.FunctionalTestCase):

    @property
    def repository(self):
        import zeit.cms.repository.interfaces
        import zope.component
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def setUp(self):
        import zeit.cms.checkout.interfaces
        import zeit.content.cp.centerpage
        import zeit.content.cp.interfaces
        import zope.component
        super(XMLTeaserBase, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.cp = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['cp']).checkout()
        factory = zope.component.getAdapter(
            self.cp['lead'], zeit.content.cp.interfaces.IElementFactory,
            name='teaser')
        self.block = factory()
        self.block.insert(0, self.repository['testcontent'])
        self.teaser = zope.component.getMultiAdapter(
            (self.block, 0), zeit.content.cp.interfaces.IXMLTeaser)


class TestXMLTeaser(XMLTeaserBase):

    def test_setting_free_teaser_should_convert(self):
        self.assertFalse(self.teaser.free_teaser)
        self.teaser.free_teaser = True
        self.assertTrue(self.teaser.free_teaser)
        self.assertTrue(self.teaser.uniqueId.startswith(
            'http://teaser.vivi.zeit.de/http://xml.zeit.de/cp#'),
            self.teaser.uniqueId)
        # Setting again doesn't harm
        self.teaser.free_teaser = True
        # Switchting off is not possible
        self.assertRaises(ValueError,
                          setattr, self.teaser, 'free_teaser', False)

    def test_original_content_should_be_part_of_cp_references(self):
        from zeit.cms.relation.interfaces import IReferences
        self.teaser.free_teaser = True
        references = IReferences(self.cp)
        self.assertEqual(
            [self.teaser.uniqueId,
             'http://xml.zeit.de/testcontent'],
            sorted(x.uniqueId for x in references))

    def test_iimages_should_contain_referenced_objects_images(self):
        from zeit.content.image.interfaces import IImages
        from zeit.cms.checkout.helper import checked_out
        import zeit.content.image.tests
        self.teaser.free_teaser = True
        group = zeit.content.image.tests.create_image_group()
        with checked_out(self.repository['testcontent']) as co:
            IImages(co).images = (group,)
        self.assertEqual((group,), IImages(self.teaser).images)

    def test_graphical_preview_should_be_provieded_if_original_does(self):
        import zeit.cms.browser.interfaces
        import zeit.content.cp.interfaces
        import zope.component
        import zope.publisher.browser
        from zeit.cms.testcontenttype.interfaces import ITestContentType
        self.teaser.free_teaser = True
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.IViviSkin)
        preview = zope.component.queryMultiAdapter(
            (self.teaser, request), name='preview')
        self.assertEqual(None, preview)
        # Provide preview
        preview_factory = mock.Mock()
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(
            preview_factory,
            (ITestContentType, zope.interface.Interface),
            zope.interface.Interface,
            name='preview')
        try:
            preview = zope.component.queryMultiAdapter(
                (self.teaser, request), name='preview')
            self.assertTrue(preview_factory.called)
            self.assertEqual(preview_factory(), preview)
        finally:
            gsm.unregisterAdapter(
                preview_factory,
                (zeit.content.cp.interfaces.IXMLTeaser, zope.interface.Interface),
                zope.interface.Interface,
                name='preview')


class TestResolver(XMLTeaserBase):

    def resolve(self, unique_id):
        from zeit.content.cp.teaser import resolve_teaser_unique_id
        return resolve_teaser_unique_id(unique_id)

    def test_unresolvable_object_should_return_none(self):
        self.assertEqual(None,
                         self.resolve('http://teaser.vivi.zeti.de/foo#bar'))

    def test_cp_from_workingcopy_should_be_used(self):
        self.teaser.teaserTitle = u'new title'
        self.teaser.free_teaser = True
        teaser = self.resolve(self.teaser.uniqueId)
        self.assertEqual(u'new title', teaser.teaserTitle)
        self.assertEqual(teaser.xml, self.teaser.xml)
        del self.repository['cp']
        teaser = self.resolve(self.teaser.uniqueId)
        self.assertEqual(teaser.xml, self.teaser.xml)

    def test_cp_from_repository_should_be_used_if_not_in_workingcopy(self):
        from zeit.cms.checkout.interfaces import ICheckinManager
        self.teaser.free_teaser = True
        ICheckinManager(self.cp).checkin()
        teaser = self.resolve(self.teaser.uniqueId)
        self.assertNotEqual(self.teaser.xml, teaser.xml)

    def test_only_centerpages_should_be_used(self):
        from zeit.cms.checkout.interfaces import ICheckinManager
        import transaction
        import zeit.connector.interfaces
        import zope.component
        self.teaser.free_teaser = True
        ICheckinManager(self.cp).checkin()
        # Change the type of the CP so we have a valid xml structure but the
        # wrong type
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.changeProperties(
            self.repository['cp'].uniqueId, {
                zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY:
                'testcontenttype'})
        transaction.commit()
        self.assertEqual(None, self.resolve(self.teaser.uniqueId))
