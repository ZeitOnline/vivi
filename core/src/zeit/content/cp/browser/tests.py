# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import contextlib
import zeit.content.cp.browser
import zeit.content.cp.testing
import zope.app.component.hooks
import zope.security.management
import zope.security.testing


def create_cp(browser, filename='island'):
    browser.open('http://localhost/++skin++cms/repository/online/2007/01')

    menu = browser.getControl(name='add_menu')
    menu.displayValue = ['CenterPage']
    browser.open(menu.value[0])

    browser.getControl('File name').value = filename
    browser.getControl('Title').value = 'Auf den Spuren der Elfen'
    browser.getControl('Ressort').displayValue = ['Reisen']
    browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
    browser.getControl(name="form.actions.add").click()



# TODO: move context managers to zeit.cms.testing

@contextlib.contextmanager
def interaction(principal_id):
    principal = zope.security.testing.Principal(u'zope.user')
    participation = zope.security.testing.Participation(principal)
    zope.security.management.newInteraction(participation)
    yield
    zope.security.management.endInteraction()


@contextlib.contextmanager
def site(root):
    old_site = zope.app.component.hooks.getSite()
    zope.app.component.hooks.setSite(root)
    yield
    zope.app.component.hooks.setSite(old_site)


def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'README.txt',
        'rule.txt',
        package=zeit.content.cp.browser)
