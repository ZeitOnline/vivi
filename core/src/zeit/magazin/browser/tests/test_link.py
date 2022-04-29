import zeit.magazin.testing


class ZMOLinkCRUD(zeit.magazin.testing.BrowserTestCase):

    def test_zmo_link_has_facebook_magazin_fields(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/magazin')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Link']
        b.open(menu.value[0])

        b.getControl('File name').value = 'link'
        b.getControl(name='form.teaserTitle').value = 'title'
        b.getControl('Ressort', index=0).displayValue = ['Leben']
        b.getControl('Link address').value = 'http://example.com'

        b.getControl('Facebook Magazin Text').value = 'mymagazin'
        b.getControl(name='form.actions.add').click()

        self.assertEndsWith('@@edit.html', b.url)
        self.assertEqual(
            'mymagazin', b.getControl('Facebook Magazin Text').value)

        b.getLink('Checkin').click()
        self.assertEllipsis('...mymagazin...', b.contents)


class ZMOFacebookFields(zeit.magazin.testing.BrowserTestCase):

    def setUp(self):
        super(ZMOFacebookFields, self).setUp()
        link = zeit.content.link.link.Link()
        link.ressort = 'Leben'
        link.teaserTitle = 'teaser'
        link.year = 2010
        link.url = 'http://example.com'
        self.repository['magazin']['mylink'] = link
        self.browser.handleErrors = False
        self.browser.open(
            'http://localhost/++skin++vivi/repository/'
            'magazin/mylink/@@checkout')

    def get_content(self):
        return zeit.cms.interfaces.ICMSWCContent(
            'http://xml.zeit.de/magazin/mylink')

    def open_form(self):
        # XXX A simple browser.reload() does not work, why?
        self.browser.open(
            'http://localhost/++skin++vivi/workingcopy/zope.user/'
            'mylink/@@edit.html')

    def test_converts_account_checkboxes_to_message_config(self):
        self.open_form()
        b = self.browser
        b.getControl('Enable Facebook Magazin').selected = True
        b.getControl('Facebook Magazin Text').value = 'fb-magazin'
        b.getControl('Apply').click()
        content = self.get_content()
        push = zeit.push.interfaces.IPushMessages(content)
        self.assertIn(
            {'type': 'facebook', 'enabled': True, 'account': 'fb-magazin',
             'override_text': 'fb-magazin'},
            push.message_config)
        self.open_form()
        self.assertTrue(b.getControl('Enable Facebook Magazin').selected)

        b.getControl('Enable Facebook Magazin').selected = False
        b.getControl('Apply').click()
        content = self.get_content()
        push = zeit.push.interfaces.IPushMessages(content)
        self.assertIn(
            {'type': 'facebook', 'enabled': False, 'account': 'fb-magazin',
             'override_text': 'fb-magazin'},
            push.message_config)

        self.open_form()
        self.assertFalse(b.getControl('Enable Facebook Magazin').selected)

    def test_stores_facebook_magazin_override_text(self):
        self.open_form()
        b = self.browser
        b.getControl('Facebook Magazin Text').value = 'facebook'
        b.getControl('Apply').click()
        content = self.get_content()
        push = zeit.push.interfaces.IPushMessages(content)
        for service in push.message_config:
            if (service['type'] != 'facebook' or
                    service.get('account') != 'fb-magazin'):
                continue
            self.assertEqual('facebook', service['override_text'])
            break
        else:
            self.fail('facebook message_config is missing')
        self.open_form()
        self.assertEqual(
            'facebook', b.getControl('Facebook Magazin Text').value)
