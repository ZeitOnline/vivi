# coding: utf-8
import unittest
import zeit.cms.interfaces


class NormalizeFilenameTest(unittest.TestCase):

    def normalize(self, text):
        # Plugin point so the JS/Selenium test can adapt this to its needs.
        return zeit.cms.interfaces.normalize_filename(text)

    def test_converts_to_lowercase(self):
        self.assertEqual('foobar', self.normalize('FooBar'))

    def test_removes_trailing_whitespace(self):
        self.assertEqual('foobar', self.normalize('foobar  '))

    def test_replaces_spaces_with_dash(self):
        self.assertEqual('foo-bar', self.normalize('foo bar'))

    def test_replaces_specialchars_with_dash(self):
        self.assertEqual('f-o', self.normalize('f&o'))

    def test_removes_specialchars_at_beginning_of_string(self):
        self.assertEqual('fo', self.normalize('&&fo'))

    def test_removes_specialchars_at_end_of_string(self):
        self.assertEqual('fo', self.normalize('fo&&'))

    def test_removes_specialchars_before_extension(self):
        self.assertEqual('fo.jpg', self.normalize('fo&&.jpg'))

    def test_collapses_consecutive_dashes(self):
        self.assertEqual('foo-bar-baz', self.normalize('foo---bar--baz'))

    def test_replaces_umlauts_with_vowels(self):
        self.assertEqual('aeaeoeuess', self.normalize('ääöüß'))

    def test_keeps_filename_extensions(self):
        self.assertEqual('foo.jpg', self.normalize('foo.jpg'))

    def test_removes_dots(self):
        self.assertEqual(
            'st-foo-bar-baz-qux', self.normalize('st.foo....bar.baz.qux'))
