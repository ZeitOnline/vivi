Text type browser integration
=============================

Add a new text[#browser]_:

>>> browser.open('http://localhost/++skin++cms/repository/2006')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Plain text']
>>> browser.handleErrors = False
>>> browser.open(menu.value[0])
>>> print browser.contents
<?xml ...
 <title>... Add plain text </title>
 ...

We're looking at the add form now. Enter a filename and a text:

>>> browser.getControl('File name').value = 'render.xslt'
>>> browser.getControl('Content').value = '''\
...     <?xml encoding="utf8"?>
...     <foo/>'''

We can choose the encoding:

>>> browser.getControl('Encoding').displayOptions
['UTF-8', 'ISO8859-15']
>>> browser.getControl('Encoding').displayValue
['UTF-8']
>>> browser.getControl('Encoding').displayValue = ['ISO8859-15']

Add now:

>>> browser.getControl('Add').click()
>>> print browser.contents
<?xml...
 <title>... Edit plain text </title>
 ...


We're now at the edit form.



.. [#browser]

    >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
    >>> browser = ExtendedTestBrowser()
    >>> browser.addHeader('Authorization', 'Basic user:userpw')
