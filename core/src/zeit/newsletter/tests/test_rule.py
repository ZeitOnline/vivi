from zeit.edit.interfaces import IRuleGlobs
import zeit.cms.testing
import zeit.edit.interfaces
import zeit.newsletter.testing
import zope.component


class RuleTest(zeit.newsletter.testing.TestCase):

    def setUp(self):
        super().setUp()
        from zeit.newsletter.newsletter import Newsletter
        from zeit.newsletter.category import NewsletterCategory
        category = NewsletterCategory()
        category.ad_middle_groups_above = 42
        category.ad_thisweeks_groups_above = 63
        self.repository['category'] = category
        self.category = self.repository['category']
        self.category['newsletter'] = Newsletter()
        self.newsletter = self.category['newsletter']
        factory = zope.component.getAdapter(
            self.newsletter.body, zeit.edit.interfaces.IElementFactory,
            name='group')
        group = factory()
        self.globs = IRuleGlobs(group)

    def test_newsletter_can_be_determined_from_body_element(self):
        self.assertTrue(self.globs.get('newsletter', False))

    def test_newsletter_retrieval_handles_non_newsletter_elements(self):
        body = self.newsletter.body
        body.__parent__ = None
        globs = IRuleGlobs(body.values()[0])
        self.assertFalse(globs.get('newsletter', False))

    def test_middle_ad_position_is_read_from_newsletter_category(self):
        self.assertEqual(43, self.globs['middle_ad_position'])

    def test_thisweeks_ad_position_is_read_from_newsletter_category(self):
        self.assertEqual(64, self.globs['thisweeks_ad_position'])

    def test_middle_ad_position_handles_non_news_letter_elements(self):
        body = self.newsletter.body
        body.__parent__ = None
        globs = IRuleGlobs(body.values()[0])
        self.assertEqual('__NONE__', globs['middle_ad_position'])

    def test_thisweeks_ad_position_handles_non_news_letter_elements(self):
        body = self.newsletter.body
        body.__parent__ = None
        globs = IRuleGlobs(body.values()[0])
        self.assertEqual('__NONE__', globs['thisweeks_ad_position'])

    def test_middle_ad_position_handles_missing_category(self):
        self.repository['newsletter'] = self.newsletter
        globs = IRuleGlobs(self.newsletter.body.values()[0])
        self.assertEqual('__NONE__', globs['middle_ad_position'])

    def test_thisweeks_ad_position_handles_missing_category(self):
        self.repository['newsletter'] = self.newsletter
        globs = IRuleGlobs(self.newsletter.body.values()[0])
        self.assertEqual('__NONE__', globs['thisweeks_ad_position'])

    def test_last_position_is_determined_from_newsletter_body(self):
        self.assertEqual(1, self.globs['last_position'])
