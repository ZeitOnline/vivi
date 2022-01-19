import os.path
import zeit.connector.testing


class FilesystemConnectorTest(zeit.connector.testing.FilesystemConnectorTest):

    def test_list_root(self):
        root = list(self.connector.listCollection('http://xml.zeit.de/'))
        for item in [
                ('2006', 'http://xml.zeit.de/2006/'),
                ('2007', 'http://xml.zeit.de/2007/'),
                ('2016', 'http://xml.zeit.de/2016/'),
                ('online', 'http://xml.zeit.de/online/'),
                ('testcontent', 'http://xml.zeit.de/testcontent'),
                ('testing', 'http://xml.zeit.de/testing/')]:
            self.assertIn(item, root)


class MetadataTest(zeit.connector.testing.FilesystemConnectorTest):

    def test_minimal_properties_if_neither_metadata_head_nor_file(self):
        feed = self.connector['http://xml.zeit.de/politik.feed']
        self.assertEqual(
            [('type', 'http://namespaces.zeit.de/CMS/meta')],
            sorted(feed.properties))

    def test_nonexistent_uniqueId_raises_KeyError(self):
        with self.assertRaises(KeyError):
            self.connector['http://xml.zeit.de/nonexistent']

    def test_metadata_read_from_metadata_file(self):
        image = self.connector['http://xml.zeit.de/2006/DSC00109_2.JPG']
        author = image.properties[
            ('author', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual('Jochen Stahnke', author)
        banner = image.properties[
            ('banner', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual('yes', banner)

    def test_metadata_read_from_content_file_as_fallback(self):
        self.assertFalse(os.path.exists(os.path.join(
            self.connector.repository_path,
            'online/2007/01/4schanzentournee-abgesang.meta')))
        article = self.connector[
            'http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang']
        author = article.properties[
            ('author', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual(' Ulrich Dehne', author)  # space is from live data
        banner = article.properties[
            ('banner', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual('yes', banner)

    def test_metadata_for_metadata_file_itself_is_unknown(self):
        meta = self.connector['http://xml.zeit.de/2007/03/group.meta']
        type_ = meta.properties[
            ('type', 'http://namespaces.zeit.de/CMS/meta')]
        self.assertEqual('unknown', type_)

    def test_imagegroup_is_a_directory_but_recognized_as_its_own_type(self):
        group = self.connector['http://xml.zeit.de/2007/03/group']
        type_ = group.properties[
            ('type', 'http://namespaces.zeit.de/CMS/meta')]
        self.assertEqual('image-group', type_)

    def test_imagegroup_has_trailing_slash_in_uniqueId(self):
        # Since XSLT expects it and the real connector does it like that.
        group = self.connector['http://xml.zeit.de/2007/03/group']
        self.assertEqual('http://xml.zeit.de/2007/03/group/', group.id)

    def test_empty_attribute_node_is_parsed_as_empty_string(self):
        image = self.connector['http://xml.zeit.de/2006/DSC00109_2.JPG']
        copyrights = image.properties[
            ('copyrights', 'http://namespaces.zeit.de/CMS/document')]
        self.assertEqual('', copyrights)

    def test_raw_files_return_dav_contenttype(self):
        css = self.connector['http://xml.zeit.de/online/2007/02/zon.css']
        self.assertEqual('text/css', css.contentType)


class CachingTest(zeit.connector.testing.FilesystemConnectorTest):

    def test_caches_properties(self):
        self.connector['http://xml.zeit.de/testcontent']
        self.assertIn(
            'http://xml.zeit.de/testcontent', self.connector.property_cache)

    def test_caches_body(self):
        self.connector['http://xml.zeit.de/testcontent'].data
        self.assertIn(
            'http://xml.zeit.de/testcontent', self.connector.body_cache)

    def test_caches_childnames(self):
        self.connector.listCollection('http://xml.zeit.de/online/')
        self.assertIn(
            'http://xml.zeit.de/online/', self.connector.child_name_cache)
