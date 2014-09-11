import zeit.content.article.testing


class FindDOMTest(zeit.content.article.testing.SeleniumTestCase):

    layer = zeit.content.article.testing.WEBDRIVER_LAYER

    def setUp(self):
        super(FindDOMTest, self).setUp()
        self.open('/@@/zeit.content.article.edit.browser.tests.fixtures'
                  '/replace.html')

    def test_no_current_selection_starts_search_at_beginning_of_node(self):
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("one"), "foo")')
        self.assertEqual(
            '0', self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            '3', self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_starts_search_at_current_selection_if_one_exists(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("two").firstChild, 4, 4)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo")')
        self.assertEqual(
            '8', self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            '11', self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_selection_outside_of_node_is_ignored(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("one").firstChild, 4, 4)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo")')
        self.assertEqual(
            '0', self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            '3', self.eval('window.getSelection().getRangeAt(0).endOffset'))
