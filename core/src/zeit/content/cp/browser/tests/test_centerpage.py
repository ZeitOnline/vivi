from unittest import mock
import zeit.content.cp.browser.testing
import zeit.content.cp.testing
import zeit.edit.interfaces
import zeit.edit.rule
import zope.component


class PublishTest(zeit.content.cp.testing.BrowserTestCase):
    """Integration test for zeit.workflow.browser.publish.Publish.

    Checks that adapter to use ValidatingWorkflow was set up correctly.

    """

    def test_validation_errors_are_displayed_during_publish(self):
        from zeit.content.cp.centerpage import CenterPage

        self.repository['centerpage'] = CenterPage()
        rm = zope.component.getUtility(zeit.edit.interfaces.IRulesManager)
        rules = [rm.create_rule(['error_if(True, "Custom Error")'], 0)]
        with mock.patch.object(zeit.edit.rule.RulesManager, 'rules', rules):
            b = self.browser
            b.open('http://localhost/++skin++vivi/repository' '/centerpage/@@publish.html')
        self.assertEllipsis('...Custom Error...', b.contents)


class PermissionsTest(zeit.content.cp.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        zeit.content.cp.browser.testing.create_cp(self.browser)
        self.browser.getLink('Checkin').click()

        self.producing = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        self.producing.login('producer', 'producerpw')

    def test_normal_user_may_not_delete(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/online/2007/01/island')
        self.assertNotIn('island/@@delete.html', b.contents)

    def test_producing_may_delete(self):
        b = self.producing
        b.open('http://localhost/++skin++vivi/repository/online/2007/01/island')
        self.assertEllipsis('...<a...island/@@delete.html...', b.contents)

    def test_normal_user_may_not_retract_via_menu_item(self):
        b = self.browser
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pi:
            pi().published = True
            b.open('http://localhost/++skin++vivi/repository/online/2007/01/' 'island')
            self.assertNotIn('island/@@retract', b.contents)

    def test_normal_user_may_not_retract_via_button(self):
        b = self.browser
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pi:
            pi().published = True
            b.open(
                'http://localhost/++skin++vivi/repository/online/2007/01/' 'island/workflow.html'
            )
            with self.assertRaises(LookupError):
                b.getControl('Save state and retract now')

    def test_producing_may_retract_via_menu_item(self):
        b = self.producing
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pi:
            pi().published = True
            b.open('http://localhost/++skin++vivi/repository/online/2007/01/' 'island')
            self.assertEllipsis('...<a...island/@@retract...', b.contents)

    def test_producing_may_retract_via_button(self):
        b = self.producing
        with mock.patch('zeit.cms.workflow.interfaces.IPublishInfo') as pi:
            pi().published = True
            b.open(
                'http://localhost/++skin++vivi/repository/online/2007/01/' 'island/workflow.html'
            )
            with self.assertNothingRaised():
                b.getControl('Save state and retract now')
