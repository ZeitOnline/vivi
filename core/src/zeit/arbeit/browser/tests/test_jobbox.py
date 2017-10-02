import zeit.arbeit.testing
import zeit.cms.testing
import zeit.content.article.testing
import zeit.arbeit.interfaces


class JobboxTickerTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.arbeit.testing.LAYER

    def test_jobboxticker_can_be_edited(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                article = zeit.content.article.testing.create_article()
                self.repository['arbeit']['article'] = article
                co = zeit.cms.checkout.interfaces.ICheckoutManager(
                    self.repository['arbeit']['article']).checkout()
                body = zeit.content.article.edit.interfaces.IEditableBody(co)
                block = body.create_item('jobboxticker')
                block.__name__ = 'blockname'
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/article'
            '/editable-body/blockname/@@edit-jobboxticker?show_form=1')
        self.assertEqual(
            ['(nothing selected)'], b.getControl('Jobbox ticker').displayValue)
        b.getControl('Jobbox ticker').displayValue = ['Homepage']
        b.getControl('Apply').click()
        b.open('@@edit-jobboxticker?show_form=1')
        self.assertEqual(
            ['Homepage'], b.getControl('Jobbox ticker').displayValue)

    def test_jobboxticker_source_has_specific_attributes(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                article = zeit.content.article.testing.create_article()
        jobbox = zeit.arbeit.interfaces.JOBBOX_TICKER_SOURCE.factory.getValues(
            article)[0]
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
