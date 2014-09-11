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

    def test_searching_backward(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("two").firstChild, 4, 4)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("two"), "foo", '
            'zeit.content.article.BACKWARD)')
        self.assertEqual(
            '0', self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            '3', self.eval('window.getSelection().getRangeAt(0).endOffset'))

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

    def test_not_found_moves_to_sibling_text(self):
        self.eval('zeit.content.article.select('
                  'window.jQuery("#three b")[0].firstChild, 0, 0)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            '1', self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            '4', self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_moves_to_sibling_element(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("one").firstChild, 4, 4)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            '"two"', self.eval(
                'window.getSelection().getRangeAt(0).startContainer'
                '.parentNode.id'))
        self.assertEqual(
            '0', self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            '3', self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_moving_to_sibling_starts_from_the_beginning(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("three").firstChild, 0, 3)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            '1', self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            '4', self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_moves_to_parent_sibling(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("list-c").firstChild, 3, 3)')
        self.eval(
            'zeit.content.article.find_next('
            'document.getElementById("content"), "foo")')
        self.assertEqual(
            '"three"', self.eval(
                'window.getSelection().getRangeAt(0).startContainer'
                '.parentNode.id'))
        self.assertEqual(
            '0', self.eval('window.getSelection().getRangeAt(0).startOffset'))
        self.assertEqual(
            '3', self.eval('window.getSelection().getRangeAt(0).endOffset'))

    def test_not_found_at_all_returns_special_value(self):
        self.eval('zeit.content.article.select('
                  'document.getElementById("three").firstChild, 0, 0)')
        self.assertEqual(
            '-1', self.eval(
                'zeit.content.article.find_next('
                'document.getElementById("content"), "nonexistent")'
                '["position"]'))
