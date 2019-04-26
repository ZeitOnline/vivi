from zeit.content.article.edit.interfaces import JOBTICKER_SOURCE
import zeit.cms.testing
import zeit.content.article.testing


class JobTickerTest(
        zeit.content.article.edit.browser.testing.BrowserTestCase):

    def test_jobticker_can_be_edited(self):
        article = zeit.content.article.testing.create_article()
        self.repository['article'] = article
        co = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['article']).checkout()
        body = zeit.content.article.edit.interfaces.IEditableBody(co)
        block = body.create_item('jobboxticker')
        block.__name__ = 'blockname'

        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/article'
            '/editable-body/blockname/@@edit-jobticker?show_form=1')
        self.assertEqual(
            ['(nothing selected)'], b.getControl('Jobbox ticker').displayValue)
        b.getControl('Jobbox ticker').displayValue = ['Homepage']
        b.getControl('Apply').click()
        b.open('@@edit-jobticker?show_form=1')
        self.assertEqual(
            ['Homepage'], b.getControl('Jobbox ticker').displayValue)

    def test_jobticker_source_has_specific_attributes(self):
        article = zeit.content.article.testing.create_article()
        jobbox = JOBTICKER_SOURCE.factory.getValues(article)[0]
        self.assertEqual(
            'http://app-cache.zeit.de/academics-hp-feed',
            jobbox.feed_url)
        self.assertEqual(
            'http://jobs.zeit.de/',
            jobbox.landing_url)
        self.assertEqual(
            'Aktuelle Jobs im ZEIT Stellenmarkt',
            jobbox.teaser)
        self.assertEqual(
            'Homepage',
            jobbox.title)
