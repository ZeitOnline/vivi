Text type browser integration
=============================

Add a new text[#browser]_:

>>> browser.open('http://localhost/++skin++cms/repository/2006')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Plain text']
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


After adding we're at the edit form:

>>> browser.getControl('Add').click()
>>> print browser.contents
<?xml...
 <title>... Edit plain text </title>
 ...


Change text and encoding and save. Note that the value which is passed between
browser and server is *always* UTF-8 regardles of the storage encoding.

>>> browser.getControl('Content').value = u'F\xfc'.encode('utf8')
>>> browser.getControl('Encoding').displayValue = ['UTF-8']
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml...
 <title>... Edit plain text </title>
 ...Updated on...


Check in (note that the contents is preformatted):

>>> browser.getLink('Checkin').click()
>>> print browser.contents
<?xml...
 <title>... View plain text </title>
 ...
        <div class="widget"><pre>Fü</pre></div>
        ...
 

Check out: 

>>> browser.getLink('Checkout').click()
>>> print browser.contents
<?xml...
 <title>... Edit plain text </title>
 ...



Verify the metdata preview:

>>> browser.open('http://localhost/++skin++cms/repository/2006/'
...              'render.xslt/metadata_preview')
>>> print browser.contents
  <div...
    <p>
      http://namespaces.zeit.de/CMS/meta type:
      text
    </p>
    ...

We have a special icon:

>>> browser.open('http://localhost/++skin++cms/repository/2006/')
>>> print browser.contents
<?xml...
       <img src="http://localhost/++skin++cms/@@/zeit-content-text-interfaces-IText-zmi_icon.png" alt="Text" width="20" height="20" border="0" />
       ...


.. [#browser]

    >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
    >>> browser = ExtendedTestBrowser()
    >>> browser.addHeader('Authorization', 'Basic user:userpw')
