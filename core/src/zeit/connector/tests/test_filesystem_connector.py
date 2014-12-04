import os.path
import zeit.connector.testing


class FilesystemConnectorTest(zeit.connector.testing.FilesystemConnectorTest):

    def test_list_root(self):
        self.assertEqual(
            [
                (u'2006', u'http://xml.zeit.de/2006'),
                (u'2007', u'http://xml.zeit.de/2007'),
                (u'online', u'http://xml.zeit.de/online'),
                (u'politik.feed', u'http://xml.zeit.de/politik.feed'),
                (u'testcontent', u'http://xml.zeit.de/testcontent'),
                (u'testing', u'http://xml.zeit.de/testing'),
                (u'wirtschaft.feed', u'http://xml.zeit.de/wirtschaft.feed'),
            ],
            list(self.connector.listCollection('http://xml.zeit.de/')))


class MetadataTest(zeit.connector.testing.FilesystemConnectorTest):

    def test_minimal_properties_if_neither_metadata_head_nor_file(self):
        feed = self.connector['http://xml.zeit.de/politik.feed']
        self.assertEqual(
            [('getlastmodified', 'DAV:'),
             ('type', 'http://namespaces.zeit.de/CMS/meta')],
            sorted(feed.properties))

    def test_nonexistent_uniqueId_raises_KeyError(self):
        with self.assertRaises(KeyError):
            self.connector['http://xml.zeit.de/nonexistent']

    def test_metadata_read_from_metadata_file(self):
        image = self.connector['http://xml.zeit.de/2006/DSC00109_2.JPG']
        author = image.properties[
            ('author', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual(u'Jochen Stahnke', author)
        banner = image.properties[
            ('banner', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual(u'yes', banner)

    def test_metadata_read_from_content_file_as_fallback(self):
        self.assertFalse(os.path.exists(os.path.join(
            self.connector.repository_path,
            'online/2007/01/4schanzentournee-abgesang.meta')))
        article = self.connector[
            'http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang']
        author = article.properties[
            ('author', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual(u' Ulrich Dehne', author)  # space is from live data
        banner = article.properties[
            ('banner', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual(u'yes', banner)

    def test_imagegroup_is_a_directory_but_recognized_as_its_own_type(self):
        group = self.connector['http://xml.zeit.de/2007/03/group']
        type_ = group.properties[
            ('type', 'http://namespaces.zeit.de/CMS/meta')]
        self.assertEqual('image-group', type_)

    def test_imagegroup_has_trailing_slash_in_uniqueId(self):
        # Since XSLT expects it and the real connector does it like that.
        group = self.connector['http://xml.zeit.de/2007/03/group']
        self.assertEqual('http://xml.zeit.de/2007/03/group/', group.id)
