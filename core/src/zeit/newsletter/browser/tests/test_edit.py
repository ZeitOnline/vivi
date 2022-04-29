import transaction
import zeit.cms.interfaces
import zeit.edit.interfaces
import zeit.newsletter.testing
import zope.component


class EditorTest(zeit.newsletter.testing.BrowserTestCase):

    def setUp(self):
        from zeit.newsletter.newsletter import Newsletter
        super(EditorTest, self).setUp()
        self.repository['newsletter'] = Newsletter()

    def test_newsletter_can_be_checked_out(self):
        self.browser.handleErrors = False
        self.browser.open(
            'http://localhost/++skin++vivi/repository/newsletter/@@checkout')


class BlockEditingTest(zeit.newsletter.testing.SeleniumTestCase):

    def setUp(self):
        super(BlockEditingTest, self).setUp()
        self.open('/repository/newsletter/@@checkout')
        # XXX without this, create_content_and_fill_clipboard raises a
        # ConflictError
        transaction.commit()

    def test_groups_should_be_addable(self):
        s = self.selenium
        s.assertElementNotPresent('css=.block.type-group')
        s.waitForElementPresent('link=*Add group')
        s.click('link=*Add group')
        s.waitForElementPresent('css=.block.type-group')

    def test_drag_content_to_group_zone_should_create_teaser_block(self):
        self.create_content_and_fill_clipboard()
        s = self.selenium

        s.waitForElementPresent('link=*Add group')
        s.click('link=*Add group')
        s.waitForElementPresent('css=.block.type-group')

        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]', 'css=div.type-group .landing-zone',
            '10,10')
        s.waitForElementPresent('css=.block.type-teaser')
        s.assertText('css=.block.type-teaser', '*c3 teaser*')

    def test_drag_content_to_teaser_zone_should_append_teaser_block(self):
        self.create_content_and_fill_clipboard()
        self.test_groups_should_be_addable()
        s = self.selenium
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c3"]', 'css=div.type-group .landing-zone',
            '10,10')
        s.waitForElementPresent('css=.block.type-teaser + .landing-zone')

        # before:
        # group
        #   Teaser (c3)
        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]', 'css=div.type-teaser + .landing-zone',
            '10,10')
        # after:
        # group
        #   Teaser (c3)
        #   Teaser (c1)

        second_teaser = 'css=.type-teaser + * + .type-teaser'
        s.waitForElementPresent(second_teaser)
        s.assertText(second_teaser, '*c1 teaser*')

    def create_two_groups(self):
        s = self.selenium

        group1 = 'css=div.type-group'
        group2 = 'css=div.type-group + div.type-group'

        s.waitForElementPresent('link=*Add group')
        s.click('link=*Add group')
        s.waitForElementPresent(group1)
        s.click('link=*Add group')
        s.waitForElementPresent(group2)

        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c1"]', group1 + ' .landing-zone', '10,10')
        s.waitForElementPresent(group1 + ' .block.type-teaser')

        s.dragAndDropToObject(
            '//li[@uniqueid="Clip/c2"]', group2 + ' .landing-zone', '10,10')
        s.waitForElementPresent(group2 + ' .block.type-teaser')

    def test_groups_should_be_sortable_with_drag_and_drop(self):
        self.create_content_and_fill_clipboard()
        self.create_two_groups()
        s = self.selenium

        group1 = 'css=div.type-group'
        group2 = 'css=div.type-group + div.type-group'

        # before:
        # group
        #   Teaser (c1)
        # group
        #   Teaser (c2)
        s.dragAndDropToObject(
            group2 + ' .dragger', group1 + ' .dragger')
        # after:
        # group
        #   Teaser (c2)
        # group
        #   Teaser (c1)

        s.waitForText(group1 + ' .block.type-teaser', '*c2*')
        s.assertText(group2 + ' .block.type-teaser', '*c1*')

    def test_drag_teaser_between_groups_should_move_it(self):
        self.create_content_and_fill_clipboard()
        self.create_two_groups()
        s = self.selenium
        s.setWindowSize(self.window_width, 700)

        group1 = 'css=div.type-group'
        group2 = 'css=div.type-group + div.type-group'

        # before:
        # group
        #   Teaser (c1)
        # group
        #   Teaser (c2)
        s.dragAndDropToObject(
            group2 + ' .type-teaser .dragger', group1 + ' .dragger')
        # after:
        # group
        #   Teaser (c2)
        #   Teaser (c1)
        # group

        second_teaser = ' .type-teaser + .type-teaser'
        s.waitForElementPresent(group1 + second_teaser)
        s.assertText(group1 + ' .block.type-teaser', '*c2*')
        s.assertText(group1 + second_teaser, '*c1*')
        s.assertElementNotPresent(group2 + ' .block.type-teaser')


class AdvertisementTest(zeit.newsletter.testing.SeleniumTestCase):

    def setUp(self):
        from zeit.newsletter.newsletter import Newsletter
        from zeit.newsletter.category import NewsletterCategory
        super(AdvertisementTest, self).setUp()
        category = NewsletterCategory()
        category.ad_middle_title = 'Some ad'
        category.ad_middle_groups_above = 0
        category.ad_middle_image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        category.ad_thisweeks_groups_above = 0
        self.repository['newsletter'] = category
        newsletter = Newsletter()
        ad_factory = zope.component.getAdapter(
            newsletter.body, zeit.edit.interfaces.IElementFactory,
            name='advertisement-middle')
        ad_factory()
        self.repository['newsletter']['one'] = newsletter
        transaction.commit()
        self.open('/repository/newsletter/one/@@checkout')

    def test_advertisement_is_wired_correctly(self):
        s = self.selenium
        s.waitForTextPresent('Some ad')
        s.waitForElementPresent('css=.newsletter-ad-image img')
