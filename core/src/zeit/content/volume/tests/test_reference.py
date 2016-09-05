import zeit.cms.content.interfaces
import zeit.content.article.edit.volume
import zeit.content.volume.testing
import zope.component


class VolumeReferenceTest(zeit.content.volume.testing.FunctionalTestCase):

    def setUp(self):
        from zeit.content.volume.volume import Volume
        super(VolumeReferenceTest, self).setUp()

        self.repository['testvolume'] = Volume()
        self.volume = self.repository['testvolume']
        self.reference_container = zeit.content.article.edit.volume.Volume(
            self.volume, self.volume.xml)

    def test_volume_can_be_adapted_to_IXMLReference(self):
        result = zope.component.getAdapter(
            self.volume,
            zeit.cms.content.interfaces.IXMLReference,
            name='related')
        self.assertEqual('volume', result.tag)
        self.assertEqual(self.volume.uniqueId, result.get('href'))

    def test_volume_can_be_adapted_to_IReference(self):
        from zeit.content.volume.interfaces import IVolumeReference

        result = zope.component.getMultiAdapter(
            (self.reference_container, self.volume.xml),
            zeit.cms.content.interfaces.IReference, name='related')

        result.teaserText = 'Test teaser'

        self.assertEqual(True, IVolumeReference.providedBy(result))
        self.assertEqual('Test teaser', result.xml.teaserText.text)
