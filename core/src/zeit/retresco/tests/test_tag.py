# coding: utf8
import unittest


class TagTest(unittest.TestCase):
    """Testing ..tag.Tag."""

    def test_from_code_generates_a_tag_object_equal_to_its_source(self):
        from ..tag import Tag
        tag = Tag(u'Vipraschül', 'Person')
        self.assertEqual(tag, Tag.from_code(tag.code))
