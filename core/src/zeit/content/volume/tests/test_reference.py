import lxml.objectify
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

    def test_volume_can_be_adapted_to_IXMLReference(self):
        result = zope.component.getAdapter(
            self.volume,
            zeit.cms.content.interfaces.IXMLReference,
            name='related')
        self.assertEqual('volume', result.tag)
        self.assertEqual(self.volume.uniqueId, result.get('href'))

    def test_volume_can_be_adapted_to_IReference(self):
        from zeit.content.volume.interfaces import IVolumeReference

        node = zope.component.getAdapter(
            self.volume, zeit.cms.content.interfaces.IXMLReference,
            name='related')
        source = zeit.content.article.edit.volume.Volume(
            None, lxml.objectify.XML('<volume/>'))
        reference = zope.component.getMultiAdapter(
            (source, node),
            zeit.cms.content.interfaces.IReference, name='related')

        reference.teaserText = 'Test teaser'

        self.assertEqual(True, IVolumeReference.providedBy(reference))
        self.assertEqual('Test teaser', reference.xml.teaserText.text)
