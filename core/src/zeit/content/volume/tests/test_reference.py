import lxml.objectify
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
        volume.teaserText = 'original'
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
        volume.teaserText = 'original'
        volume.product = zeit.cms.content.sources.Product('ZEI')
        self.repository['2015'] = Folder()
        self.repository['2015']['01'] = Folder()
        self.repository['2015']['01']['ausgabe'] = volume
        self.repository['2015']['01']['index'] = zeit.content.cp.centerpage.CenterPage()

        reference = zope.component.getAdapter(
            volume, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEqual(volume.teaserText, reference.description)

    def test_volume_can_be_adapted_to_IReference(self):
        from zeit.content.volume.interfaces import IVolumeReference

        node = zope.component.getAdapter(
            self.volume, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        source = zeit.content.article.edit.volume.Volume(None, lxml.objectify.XML('<volume/>'))
        reference = zope.component.getMultiAdapter(
            (source, node), zeit.cms.content.interfaces.IReference, name='related'
        )
        self.assertEqual(True, IVolumeReference.providedBy(reference))

    def test_teasertext_can_be_overridden(self):
        node = zope.component.getAdapter(
            self.volume, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        source = zeit.content.article.edit.volume.Volume(None, lxml.objectify.XML('<volume/>'))
        reference = zope.component.getMultiAdapter(
            (source, node), zeit.cms.content.interfaces.IReference, name='related'
        )
        self.assertEqual('original', reference.teaserText)
        reference.teaserText = 'local'
        self.assertEqual('local', reference.teaserText)
        reference.teaserText = None
        self.assertEqual('original', reference.teaserText)
