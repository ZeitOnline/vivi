# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.edit.rule import Rule
import zeit.content.article.testing


class RuleTest(zeit.content.article.testing.FunctionalTestCase):

    def test_article_glob_should_apply_to_block(self):
        block = self.get_factory(self.get_article(), 'p')()
        r = Rule("""
applicable(article)
error_if(True, u'foo')
""")
        s = r.apply(block)
        self.assertEquals(zeit.edit.rule.ERROR, s.status)
