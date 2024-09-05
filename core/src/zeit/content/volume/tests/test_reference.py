import lxml.builder
import zope.component

import zeit.cms.content.interfaces
import zeit.content.article.edit.volume
import zeit.content.cp.centerpage
import zeit.content.volume.testing


class VolumeReferenceTest(zeit.content.volume.testing.FunctionalTestCase):
    def setUp(self):
        from zeit.content.volume.volume import Volume

        super().setUp()
        volume = Volume()
        volume.volume_note = 'original'
        self.repository['testvolume'] = volume
        self.volume = self.repository['testvolume']

    def test_volume_can_be_adapted_to_IXMLReference(self):
        reference = zope.component.getAdapter(
            self.volume, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEqual('volume', reference.tag)
        self.assertEqual(self.volume.uniqueId, reference.get('href'))

    def test_reference_honors_ICommonMetadata_xml_format(self):
        from zeit.cms.repository.folder import Folder
        from zeit.content.volume.volume import Volume

        volume = Volume()
        volume.year = 2015
        volume.volume = 1
        volume.volume_note = 'original'
        volume.product = zeit.cms.content.sources.Product('ZEI')
        self.repository['2015'] = Folder()
        self.repository['2015']['01'] = Folder()
        self.repository['2015']['01']['ausgabe'] = volume
        self.repository['2015']['01']['index'] = zeit.content.cp.centerpage.CenterPage()

        reference = zope.component.getAdapter(
            volume, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEqual(
            '<volume href="http://xml.zeit.de/2015/01/ausgabe"/>',
            zeit.cms.testing.xmltotext(reference),
        )

    def test_volume_can_be_adapted_to_IReference(self):
        from zeit.content.volume.interfaces import IVolumeReference

        node = zope.component.getAdapter(
            self.volume, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        source = zeit.content.article.edit.volume.Volume(None, lxml.builder.E.volume())
        reference = zope.component.getMultiAdapter(
            (source, node), zeit.cms.content.interfaces.IReference, name='related'
        )
        self.assertEqual(True, IVolumeReference.providedBy(reference))

    def test_volume_note_can_be_overridden(self):
        node = zope.component.getAdapter(
            self.volume, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        source = zeit.content.article.edit.volume.Volume(None, lxml.builder.E.volume())
        reference = zope.component.getMultiAdapter(
            (source, node), zeit.cms.content.interfaces.IReference, name='related'
        )
        self.assertEqual('original', reference.volume_note)
        reference.volume_note = 'local'
        self.assertEqual('local', reference.volume_note)
        reference.volume_note = None
        self.assertEqual('original', reference.volume_note)
