from zeit.edit.rule import Rule
import zeit.cms.interfaces
import zeit.content.article.testing
import zeit.edit.interfaces


class RuleTest(zeit.content.article.testing.FunctionalTestCase):

    def test_article_glob_should_apply_to_block(self):
        block = self.get_factory(self.get_article(), 'p')()
        r = Rule("""
applicable(article)
error_if(True, u'foo')
""")
        s = r.apply(block, zeit.edit.interfaces.IRuleGlobs(block))
        self.assertEquals(zeit.edit.rule.ERROR, s.status)

    def test_IReference_content_returns_referenced_object(self):
        self.repository['info'] = zeit.content.infobox.infobox.Infobox()
        block = self.get_factory(self.get_article(), 'infobox')()
        block.references = self.repository['info']
        r = Rule("""
from zeit.content.infobox.interfaces import IInfobox
applicable(True)
error_if(IInfobox.providedBy(content[0]), u'foo')
""")
        s = r.apply(block, zeit.edit.interfaces.IRuleGlobs(block))
        self.assertEquals(zeit.edit.rule.ERROR, s.status)

    def test_IImage_content_returns_referenced_object(self):
        block = self.get_factory(self.get_article(), 'image')()
        image = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        block.references = block.references.create(
            zeit.cms.interfaces.ICMSContent(image))
        r = Rule("""
from zeit.content.image.interfaces import IImage
applicable(True)
error_if(IImage.providedBy(content[0]), u'foo')
""")
        s = r.apply(block, zeit.edit.interfaces.IRuleGlobs(block))
        self.assertEquals(zeit.edit.rule.ERROR, s.status)
