import mock
import zeit.content.cp.testing
import zope.component


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
        import zeit.edit.interfaces
        super(XMLTeaserBase, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.cp = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['cp']).checkout()
        factory = zope.component.getAdapter(
            self.cp['lead'], zeit.edit.interfaces.IElementFactory,
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

    def test_update_metadata_uses_free_teaser_not_referenced_object(self):
        self.teaser.free_teaser = True
        self.teaser.teaserSupertitle = 'teaserSupertitle'
        UNUSED_EVENT = None
        zeit.content.cp.centerpage.update_centerpage_on_checkin(
            self.cp, UNUSED_EVENT)
        self.assertEqual('teaserSupertitle', self.teaser.teaserSupertitle)

    def test_commonmetadata_fields_xmlteaser_doesnt_have_should_delegate(self):
        from zeit.cms.checkout.helper import checked_out
        with checked_out(self.repository['testcontent']) as co:
            co.title = 'original'
        self.teaser.free_teaser = True
        self.assertEqual('original', self.teaser.title)

    def test_cm_fields_xmlteaser_doesnt_have_should_return_their_default(self):
        self.assertEqual((), self.teaser.authorships)

    def test_iimages_should_contain_referenced_objects_image(self):
        from zeit.content.image.interfaces import IImages
        from zeit.cms.checkout.helper import checked_out
        import zeit.content.image.testing
        self.teaser.free_teaser = True
        group = zeit.content.image.testing.create_image_group()
        with checked_out(self.repository['testcontent']) as co:
            IImages(co).image = group
        self.assertEqual(group, IImages(self.teaser).image)

    def test_graphical_preview_should_be_provieded_if_original_does(self):
        import zeit.cms.browser.interfaces
        import zeit.content.cp.interfaces
        import zope.component
        import zope.publisher.browser
        from zeit.cms.testcontenttype.interfaces import IExampleContentType
        self.teaser.free_teaser = True
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSSkin)
        preview = zope.component.queryMultiAdapter(
            (self.teaser, request), name='preview')
        self.assertEqual(None, preview)
        # Provide preview
        preview_factory = mock.Mock()
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerAdapter(
            preview_factory,
            (IExampleContentType, zope.interface.Interface),
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
                (zeit.content.cp.interfaces.IXMLTeaser,
                 zope.interface.Interface),
                zope.interface.Interface,
                name='preview')

    def test_rendered_xml_has_correct_href(self):
        self.teaser.free_teaser = True
        self.cp = zeit.cms.checkout.interfaces.ICheckinManager(
            self.cp).checkin()

        # Free teasers are looked up in the workingcopy first, but since the
        # IRenderedXML code is used from zeit.frontend where there is no
        # interaction, so we must make sure it works without one.
        zope.security.management.endInteraction()
        xml = zeit.content.cp.interfaces.IRenderedXML(
            self.cp['lead'].values()[0])
        self.assertEqual(
            'http://xml.zeit.de/testcontent', xml.block.get('href'))

    def test_free_teaser_implements_eq_and_hash_via_uniqueId(self):
        teaser = zope.component.getMultiAdapter(
            (self.block, 0), zeit.content.cp.interfaces.IXMLTeaser)
        self.assertEqual(self.teaser, teaser)
        self.assertIn(teaser, set([self.teaser]))


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
        # ICP2015 is-a ICenterPage, but we need a non-cp content for this test.
        zope.interface.noLongerProvides(
            self.cp, zeit.content.cp.interfaces.ICP2015)
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
