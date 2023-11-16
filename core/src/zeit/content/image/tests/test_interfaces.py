import unittest


class TestUniqueViewportAndMasterImageConstraint(unittest.TestCase):
    def test_succeeds_for_empty_tuple(self):
        from ..interfaces import unique_viewport_and_master_image

        self.assertEqual(True, unique_viewport_and_master_image(()))

    def test_succeeds_for_unique_combinations(self):
        from ..interfaces import unique_viewport_and_master_image

        self.assertEqual(
            True, unique_viewport_and_master_image((('desktop', 'image1'), ('mobile', 'image2')))
        )

    def test_raises_DuplicateViewport_if_viewport_is_used_multiple_times(self):
        from ..interfaces import DuplicateViewport
        from ..interfaces import unique_viewport_and_master_image

        with self.assertRaises(DuplicateViewport):
            unique_viewport_and_master_image((('desktop', 'image1'), ('desktop', 'image2')))

    def test_raises_DuplicateImage_if_masterimage_is_used_multiple_times(self):
        from ..interfaces import DuplicateImage
        from ..interfaces import unique_viewport_and_master_image

        with self.assertRaises(DuplicateImage):
            unique_viewport_and_master_image((('desktop', 'image'), ('mobile', 'image')))
