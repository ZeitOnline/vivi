# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import contextlib
import lxml.cssselect
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


def create_block_in_mosaic(browser, block_type, index=0):
    old_strict = browser.xml_strict
    browser.xml_strict = True
    select = lxml.cssselect.CSSSelector(
        '.action-teaser-mosaic-module-droppable[cms|create-block-url]')
    nsmap = {'cms': 'http://namespaces.gocept.com/zeit-cms'}
    drop_url = browser.etree.xpath(select.path, namespaces=nsmap)[index].get(
        '{http://namespaces.gocept.com/zeit-cms}create-block-url')
    browser.open(drop_url + '?block_type=' + block_type)
    browser.xml_strict = old_strict


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
        'landing.txt',
        'library.txt',
        'rule.txt')
