# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.content.article.testing
import zeit.cms.testing


class SaveTextTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def get_view(self, body=None):
        from zeit.content.article.browser.edit import SaveText
        import lxml.objectify
        import zeit.content.article.article
        import zeit.content.article.edit.body
        if not body:
            body  = ("<division><p>Para 1</p><p>Para 2</p></division>"
                     "<division><p>Para 3</p><p>Para 4</p></division>")
        article = zeit.content.article.article.Article()
        article.xml.body = lxml.objectify.XML(
            '<body>%s</body>' % body)
        for division in article.xml.body.findall('division'):
            division.set('type', 'page')
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        self.uuid = mock.Mock()
        self.uuid.side_effect = lambda: self.uuid.call_count
        with mock.patch('uuid.uuid4', new=self.uuid):
            body.keys()
        view = SaveText()
        view.context = body
        view.request = mock.Mock()
        view.request.form = {}
        return view

    def test_update_should_remove_given_paragrahs(self):
        view = self.get_view()
        self.assertEqual(['2', '3', '4', '5', '6'], view.context.keys())
        view.request.form['paragraphs'] = ['5', '6']
        view.request.form['text'] = ''
        view.update()
        self.assertEqual(['2', '3', '4'], view.context.keys())

    def test_update_should_add_new_paragraphs_where_old_where_removed(self):
        view = self.get_view()
        view.request.form['paragraphs'] = ['3']
        view.request.form['text'] = ['Hinter', 'den', 'Wortbergen']
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual(['2', '7', '8', '9', '4', '5', '6'],
                         view.context.keys())

    def test_update_should_append_when_no_paragraphs_are_replaced(self):
        view = self.get_view()
        view.request.form['paragraphs'] = []
        view.request.form['text'] = ['Hinter', 'den', 'Wortbergen']
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual(['2', '3', '4', '5', '6', '7', '8', '9'],
                         view.context.keys())

    def test_update_should_remove_empty_paragraphs(self):
        view = self.get_view()
        view.request.form['paragraphs'] = []
        view.request.form['text'] = ['Hinter', 'den', ' ', 'Wortbergen']
        with mock.patch('uuid.uuid4', new=self.uuid):
            view.update()
        self.assertEqual(['2', '3', '4', '5', '6', '7', '8', '9'],
                         view.context.keys())
