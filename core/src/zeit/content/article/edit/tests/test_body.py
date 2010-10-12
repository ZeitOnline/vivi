# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest


class TesstContainer(unittest.TestCase):

    def get_body(self, body=None):
        import lxml.objectify
        import zeit.content.article.article
        import zeit.content.article.edit.body
        if not body:
            body  = ("<division><p>Para1</p><img/></division>"
                     "<division><p>Para2</p><foo/></division>")
        article = zeit.content.article.article.Article()
        article.xml.body = lxml.objectify.XML(
            '<body>%s</body>' % body)
        for division in article.xml.body.findall('division'):
            division.set('type', 'page')
        return zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)

    def test_keys_contain_division_contents(self):
        body = self.get_body()
        # The first division is omitted, thus only 5 keys
        self.assertEqual(5, len(body.keys()))
        self.assertEqual([u'division[1].*[1]',
                          u'division[1].*[2]',
                          u'division[2]',
                          u'division[2].*[1]',
                          u'division[2].*[2]'],
                         body.keys())

    def test_deleteing_division_should_merge_contained_paragraphs(self):
        pass
