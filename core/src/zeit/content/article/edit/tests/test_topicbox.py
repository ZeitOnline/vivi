import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.edit.interfaces
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType


class TestTopicbox(zeit.content.article.testing.FunctionalTestCase):

    def get_topicbox(self):
        from zeit.content.article.edit.topicbox import Topicbox
        import lxml.objectify
        box = Topicbox(None, lxml.objectify.E.topicbox())
        return box

    def get_cp(self, content=None):
        import zeit.content.cp.centerpage
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        if content:
            region = self.repository['cp'].create_item('region')
            area = region.create_item('area')
            for cont in content:
                teaser = area.create_item('teaser')
                teaser.insert(0, cont)
        return self.repository['cp']

    def test_topicbox_values_does_not_contain_empty_reference(self):
        box = self.get_topicbox()
        article = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/online/2007/01/Somalia")
        box.first_reference = article
        self.assertEqual([article, ], list(box.values()))

    def test_empty_referenced_cp_has_no_values(self):
        box = self.get_topicbox()
        cp = self.get_cp()
        box.first_reference = cp
        self.assertEqual(cp, box.referenced_cp)
        self.assertEqual([], list(box.values()))

    def test_box_uses_cp_content(self):
        box = self.get_topicbox()
        article = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/online/2007/01/Somalia")
        cp = self.get_cp(content=[article, ])
        box.first_reference = cp
        self.assertEqual([article], list(box.values()))

    def test_box_uses_first_three_cp_entries(self):
        content = []
        article_names = ['foo', 'bar', 'baz', 'qux']
        for name in article_names:
            self.repository[name] = ExampleContentType()
            content.append(self.repository[name])
        box = self.get_topicbox()
        cp = self.get_cp(content=content)
        box.first_reference = cp
        self.assertEqual(cp, box.referenced_cp)
        self.assertEqual(content[:3], list(box.values()))

    def test_box_if_cp_is_referenced_rest_is_ignored(self):
        self.repository['foo'] = ExampleContentType()
        box = self.get_topicbox()
        cp = self.get_cp(content=[self.repository['foo'],])
        box.first_reference = cp
        box.second_reference = zeit.cms.interfaces.ICMSContent(
            "http://xml.zeit.de/online/2007/01/Somalia")
        self.assertEqual([self.repository['foo'], ], list(box.values()))
