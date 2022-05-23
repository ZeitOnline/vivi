Text type browser integration
=============================

Add a new text:

>>> import zeit.cms.testing
>>> browser = zeit.cms.testing.Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')
>>> browser.open('http://localhost/++skin++cms/repository/2006')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Plain text']
>>> browser.open(menu.value[0])
>>> print(browser.contents)
<?xml ...
 <title>... Add plain text </title>
 ...

We're looking at the add form now. Enter a filename and a text:

>>> browser.getControl('File name').value = 'render.xslt'
>>> browser.getControl('Content').value = '''\
...     <?xml encoding="utf8"?>
...     <foo/>'''

After adding we're at the edit form:

>>> browser.getControl('Add').click()
>>> print(browser.contents)
<?xml...
 <title>... Edit plain text </title>
 ...

>>> browser.getControl('Content').value = 'F\xfc'.encode('utf8')
>>> browser.getControl('Apply').click()
>>> print(browser.contents)
<?xml...
 <title>... Edit plain text </title>
 ...Updated on...


Check in (note that the contents is preformatted):

>>> browser.getLink('Checkin').click()
>>> print(browser.contents)
<?xml...
 <title>... View plain text </title>
 ...
        <div class="widget"><pre>Fü</pre></div>
        ...
 

Check out: 

>>> browser.getLink('Checkout').click()
>>> print(browser.contents)
<?xml...
 <title>... Edit plain text </title>
 ...


MIME type is editable:

>>> browser.getControl('Mime Type').value = 'application/json'
>>> browser.getControl('Apply').click()
>>> print(browser.contents)
<...Updated on...
>>> browser.getControl('Mime Type').value
'application/json'

>>> browser.getLink('Checkin').click()
>>> print(browser.contents)
<...application/json...


Verify the metdata preview:

>>> browser.open('http://localhost/++skin++cms/repository/2006/'
...              'render.xslt/metadata_preview')
>>> print(browser.contents)
  <div...
    <p>
      http://namespaces.zeit.de/CMS/meta type:
      text
    </p>
    ...

We have a special icon:

>>> browser.open('http://localhost/++skin++cms/repository/2006/')
>>> print(browser.contents)
<?xml...
       <img src="http://localhost/++skin++cms/@@/zeit-content-text-interfaces-IText-zmi_icon.png" alt="Text" width="20" height="20" border="0" />
       ...
