import lxml.cssselect


def create_cp(browser, filename='island'):
    browser.open('http://localhost/++skin++cms/repository/online/2007/01')

    menu = browser.getControl(name='add_menu')
    menu.displayValue = ['CenterPage']
    browser.open(menu.value[0])

    browser.getControl('File name').value = filename
    browser.getControl('Title').value = 'Auf den Spuren der Elfen'
    browser.getControl('Ressort').displayValue = ['Reisen']
    browser.getControl(name="form.actions.add").click()


def create_block_in_mosaic(browser, block_type, index=0):
    old_strict = browser.xml_strict
    browser.xml_strict = True
    select = lxml.cssselect.CSSSelector(
        '.action-cp-module-droppable[cms|create-block-url]')
    nsmap = {'cms': 'http://namespaces.gocept.com/zeit-cms'}
    drop_url = browser.etree.xpath(select.path, namespaces=nsmap)[index].get(
        '{http://namespaces.gocept.com/zeit-cms}create-block-url')
    browser.open(drop_url + '?block_type=' + block_type)
    browser.xml_strict = old_strict
