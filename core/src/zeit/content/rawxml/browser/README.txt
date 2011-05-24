Raw XML browser access
======================

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

>>> browser.open('http://localhost/++skin++cms/repository')

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
>>> browser.handleErrors = False
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
      <img src="http://localhost/++skin++cms/@@/zeit-content-rawxml-interfaces-IRawXML-zmi_icon.png" alt="RawXML" width="18" height="18" border="0" />
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

There is an edit tab:

>>> browser.getLink('Edit', index=1)
<Link text='Edit' url='http://localhost/++skin++cms/workingcopy/zope.user/rawxml/@@edit.html'>


After checking in we see the read/only view:

>>> browser.getLink('Checkin').click()
>>> print browser.contents
<?xml ...
    <title>... View Raw XML </title>
    ...
        <div class="widget"><span class="h_tag">&lt;block&gt;</span><span class="h_default"><br/>
&nbsp;&nbsp;</span><span class="h_tag">&lt;feed</span><span class="h_tagend">/&gt;</span><span class="h_default"><br/>
</span><span class="h_tag">&lt;/block&gt;</span><span class="h_default"><br/>
</span></div>
...
>>> print browser.url
http://localhost/++skin++cms/repository/rawxml/@@view.html

There is also a default view:

>>> browser.open('http://localhost/++skin++cms/repository/rawxml')
>>> print browser.title.strip()
This is raw feed foo – View Raw XML

Let's syndicate. Add a channel to the targets first:

>>> bookmark = browser.url
>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Remember as syndication target').click()
>>> browser.open(bookmark)
>>> browser.getLink('Syndicate').click()
>>> checkbox = browser.getControl(
...     name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> checkbox.value = True
>>> browser.getControl('Syndicate').click()
>>> print browser.contents
<?xml ...
    <div id="messages" class="haveMessages">
      <ul>
        <li class="message">"rawxml" has been syndicated to politik.feed</li>
      </ul>
    ...
