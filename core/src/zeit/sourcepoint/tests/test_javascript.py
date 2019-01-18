from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.testing
import zeit.sourcepoint.interfaces
import zeit.sourcepoint.testing
import zope.component


class JavascriptDownload(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.sourcepoint.testing.LAYER

    def test_latest_version_sorts_folder_items(self):
        folder = self.repository['sourcepoint']
        folder['msg_20190110.js'] = ExampleContentType()
        folder['msg_20190113.js'] = ExampleContentType()
        folder['msg_20190117.js'] = ExampleContentType()
        folder['msg_201901170815.js'] = ExampleContentType()
        folder['msg_201901171230.js'] = ExampleContentType()

        js = zope.component.getUtility(zeit.sourcepoint.interfaces.IJavaScript)
        self.assertEqual('http://xml.zeit.de/sourcepoint/msg_201901171230.js',
                         spjs.latest_version.uniqueId)
