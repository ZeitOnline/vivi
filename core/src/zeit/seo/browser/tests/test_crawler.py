import transaction

from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.interfaces import IExampleContentType
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.link.interfaces import ILink
from zeit.seo.interfaces import ISEO
import zeit.seo.testing


class EnableCrawler(zeit.seo.testing.SeleniumTestCase):
    login_as = 'seo:seopw'

    def test_renames_content_and_creates_redirect(self):
        IPublishInfo(ICMSContent('http://xml.zeit.de/testcontent')).urgent = True
        s = self.selenium
        self.open('/repository/testcontent', self.login_as)
        s.click('link=View SEO')
        s.click('id=form.actions.enable-crawler')

        s.waitForElementPresent('css=ol#worklist')
        s.waitForElementPresent('css=li.busy[action=start_job]')
        s.waitForElementNotPresent('css=li.busy[action=start_job]')
        s.waitForLocation('*/testcontent-gxe')  # wait for reload

        transaction.abort()
        link = ICMSContent('http://xml.zeit.de/testcontent')
        self.assertTrue(ILink.providedBy(link))
        self.assertTrue(IPublishInfo(link).published)
        article = ICMSContent('http://xml.zeit.de/testcontent-gxe')
        self.assertTrue(IExampleContentType.providedBy(article))
        self.assertTrue(IPublishInfo(article).published)
        self.assertTrue(ISEO(article).crawler_enabled)
