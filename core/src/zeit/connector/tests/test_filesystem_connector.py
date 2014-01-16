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
