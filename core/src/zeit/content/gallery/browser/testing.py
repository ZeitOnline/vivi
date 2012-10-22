# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path


def add_folder(browser, name):
    menu = browser.getControl(name='add_menu')
    menu.displayValue = ['Folder']
    browser.open(menu.value[0])
    browser.getControl('File name').value = name
    browser.getControl('Add').click()


def add_image(browser, name):
    gallery_url = browser.url
    menu = browser.getControl(name='add_menu')
    menu.displayValue = ['Image (single)']
    browser.open(menu.value[0])
    test_file = os.path.join(os.path.dirname(__file__),
                             'testdata', name)
    test_data = open(test_file, 'rb')
    file_control = browser.getControl(name='form.blob')
    file_control.add_file(test_data, 'image/jpeg', name)
    browser.getControl(name='form.copyrights.0..combination_00').value = (
        'ZEIT ONLINE')
    browser.getControl(name='form.copyrights.0..combination_01').value = (
        'http://www.zeit.de/')
    browser.getControl(name='form.actions.add').click()
    browser.getLink('Checkin').click()
    url = browser.url
    browser.open(gallery_url)
    return url
