import lxml.objectify
import zeit.content.cp.testing


class UnknownBlockTest(zeit.content.cp.testing.FunctionalTestCase):
    def test_uses_cp_specific_unknown_block(self):
        xml = lxml.objectify.fromstring(
            """
        <region xmlns:cp="http://namespaces.zeit.de/CMS/cp">
          <something cp:__name__="foo"/>
        </region>
        """
        )
        cp = zeit.content.cp.centerpage.CenterPage()
        area = cp.create_item('region').create_item('area')
        area.xml = xml
        self.assertTrue(zeit.edit.interfaces.IUnknownBlock.providedBy(area['foo']))
        self.assertTrue(zeit.content.cp.interfaces.IBlock.providedBy(area['foo']))
