import zeit.content.article.article
import zeit.content.article.edit.interfaces
import zeit.content.article.testing
import zeit.edit.interfaces


class TestTopicbox(zeit.content.article.testing.FunctionalTestCase):

    def get_topicbox(self):
        from zeit.content.article.edit.topicbox import Topicbox
        import lxml.objectify
        box = Topicbox(None, lxml.objectify.E.topicbox())
        return box

    def get_cp(self, content=None):
        import zeit.content.cp.centerpage
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
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
        self.assertEqual([], list(cp.values()))
