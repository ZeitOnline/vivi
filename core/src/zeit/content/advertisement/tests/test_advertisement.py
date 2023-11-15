import zeit.content.advertisement.testing


class AdvertisementTest(zeit.content.advertisement.testing.FunctionalTestCase):
    def test_image_of_advertisement_can_be_retrieved_via_IImages(self):
        from zeit.content.advertisement.advertisement import Advertisement

        advertisement = Advertisement()
        image = self.repository['2006']['DSC00109_2.JPG']
        advertisement.image = image

        images = zeit.content.image.interfaces.IImages(advertisement)
        self.assertIsNotNone(images.image)
        self.assertEqual(images.image, image)
