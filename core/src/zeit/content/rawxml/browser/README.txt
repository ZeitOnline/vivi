Raw XML browser access
======================

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

>>> browser.open('http://localhost/++skin++cms')

Add a raw xml:

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Raw XML']
>>> url = menu.value[0]
>>> browser.open(menu.value[0])
>>> print browser.contents
<?xml ...
    <title>... Add Raw XML </title>
    ...
>>> browser.getControl('File name').value = 'rawxml'
>>> browser.getControl('Title').value = 'This is raw feed foo'
>>> browser.getControl('XML').value = '<block><feed/></block>'
>>> browser.getControl("Add").click()

We're now at the edit page:

>>> print browser.contents
<?xml ...
    <title>... Edit Raw XML </title>
    ...


In the edited documents panel we see the title of the object and its icon:

>>> print browser.contents
<?xml ...
  <tr>
    <td>
      <img src="http://localhost/++skin++cms/@@/zeit-content-rawxml-interfaces-IRawXML-zmi_icon.png" alt="RawXML" width="20" height="20" border="0" />
    </td>
    <td>
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/rawxml/edit.html">This is raw feed foo</a>
    </td>
    <td>
      <span class="URL">http://localhost/++skin++cms/workingcopy/zope.user/rawxml</span><span class="uniqueId">http://xml.zeit.de/rawxml</span>
    </td>
  </tr>
  ...



The xml is pretty printed:

>>> print browser.getControl('XML').value
<block>
  <feed/>
</block>


Set the omit root flag: 

>>> browser.getControl('Omit root').selected = True

There is an edit tab:

>>> browser.getLink('Edit', index=1)
<Link text='Edit' url='http://localhost/++skin++cms/workingcopy/zope.user/rawxml/@@edit.html'>



After checking in we see the read/only view:

>>> browser.getLink('Checkin').click()
>>> print browser.contents
<?xml ...
    <title>... View Raw XML </title>
    ...
        <div class="widget"><pre>&lt;block&gt;
  &lt;feed/&gt;
&lt;/block&gt;
</pre></div>
...



