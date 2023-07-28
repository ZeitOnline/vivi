import importlib.resources


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
    file_control = browser.getControl(name='form.blob')
    file_control.add_file((importlib.resources.files(
        __package__) / f'testdata/{name}').read_bytes(), 'image/jpeg', name)
    browser.getControl(name='form.copyright.combination_00').value = (
        'ZEIT ONLINE')
    browser.getControl(name='form.copyright.combination_01').displayValue = (
        ['dpa'])
    browser.getControl(name='form.copyright.combination_03').value = (
        'http://www.zeit.de/')
    browser.getControl(name='form.actions.add').click()
    browser.getLink('Checkin').click()
    url = browser.url
    browser.open(gallery_url)
    return url
