import zope.publisher.browser

import zeit.cms.content.sources
import zeit.content.volume.browser.reference
import zeit.content.volume.testing
import zeit.content.volume.volume


class ReferenceDisplayTest(zeit.content.volume.testing.FunctionalTestCase):
    def get_display_view(self, cover_image=True):
        from zeit.content.image.testing import create_image_group
        from zeit.content.volume.reference import RelatedReference, XMLRelatedReference

        self.repository['imagegroup'] = create_image_group()

        volume = zeit.content.volume.volume.Volume()
        volume.year = 2014
        volume.volume = 49
        volume.product = zeit.cms.content.sources.Product('ZEI')
        if cover_image:
            volume.set_cover('portrait', volume.product.id, self.repository['imagegroup'])
        self.repository['volume'] = volume

        xml = XMLRelatedReference(self.repository['volume'])
        reference = RelatedReference(volume, xml)
        view = zeit.content.volume.browser.reference.Display()
        view.context = reference
        view.request = zope.publisher.browser.TestRequest()

        return view

    def test_display_shows_year_and_volume(self):
        self.assertEqual(
            'Die Zeit, Jahrgang: 2014, Ausgabe 49', self.get_display_view().description()
        )

    def test_display_shows_cover_image(self):
        self.assertEllipsis(
            '<img src=".../imagegroup/thumbnails/original/@@raw" ... />',
            self.get_display_view().cover_image(),
        )

    def test_display_shows_no_cover_image_if_not_available(self):
        self.assertEllipsis('', self.get_display_view(cover_image=False).cover_image())
