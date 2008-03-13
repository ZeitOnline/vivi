================
Syndcation Views
================

Create a browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

Syndication is only possible for repository content. To syndicate a user
chooses one or more syndication targets. The user can add any feed to "his
targets".

Syndication
===========

Let's open a dockument in the repository and look at its `metadata_preview`
page. We do have a syndication link there:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> link = browser.getLink('Syndicate').click()

After clicking `Syndicate` we look at a page showing possible syndication
targets:

>>> print browser.contents
<?xml ...
<!DOCTYPE html...
    <p>
     You need to select a feed as a syndication target first, before you
     can syndicate this article.
    </p>
...


The list is empty, because the user hasn't chosen any targets. Let's do that
now:

>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Remember as syndication target').click()

Visit the syndication page again:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> link = browser.getLink('Syndicate').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html...
<table>
  <thead>
    ...
    <th>
      Position
    </th>
    ...
  </thead>
  <tbody>
    <tr>
      <td>
        <input ... />
      </td>
      <td>
      </td>
      <td>
        Politik
      </td>
      <td>
        <a href="...">...politik.feed</a>
      </td>
      <td>
      </td>
    </tr>
  </tbody>
</table>
...
  

After syndication to the `Politik` feed the document is at the first posistion
in the feed:

>>> politik_checkbox = browser.getControl(
...    name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> politik_checkbox.value = True
>>> browser.getControl('Syndicate').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html...
<table>
  <thead>
    ...
    <th>
      Position
    </th>
    ...
  </thead>
  <tbody>
    <tr>
      <td>
        <input ... />
      </td>
      <td>
      </td>
      <td>
        Politik
      </td>
      <td>
        <a href="...">...politik.feed</a>
      </td>
      <td>
        1
      </td>
    </tr>
  </tbody>
</table>
...

Let's look at the feed in the repository, to make sure our document is really
in there:

>>> browser.getLink('http://xml.zeit.de/politik.feed').click()
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
  <td>
    <a href="...">rauchen-verbessert-die-welt</a>
  </td>
...

Locking information should also be displayed in the syndication manager:

>>> browser.open('http://localhost/++skin++cms/repository/wirtschaft.feed/@@view.html')
>>> browser.getLink("Checkout").click()
>>> browser.getLink("Remember as syndication target").click()
>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> browser.getLink('Syndicate').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html...
<div id="edit-form">
<h1>Syndicate rauchen-verbessert-die-welt</h1>
<form method="POST">
  ...
    <tr>
      <td>
        <input .../>
      </td>
      <td>
        <img src="/@@/zeit.cms/icons/lock-closed-mylock.png" title="Von Ihnen gesperrt" />
      </td>
      <td>
        Wirtschaft
      </td>
      <td>
        <a href="...">...wirtschaft.feed</a>
      </td>
      <td>
      </td>
...


Feeds
=====

Let's create a new feed in the repository:

>>> browser.open('http://localhost/++skin++cms/repository/2006')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Feed']
>>> browser.open(menu.value[0])

We are looking at the add form now. Fill in the title and add the feed:

>>> browser.getControl(name='form.title').value = 'Zuender'
>>> browser.getControl(name='form.__name__').value = 'zuender'
>>> browser.getControl(name='form.object_limit').value = '20'
>>> browser.getControl(name='form.actions.add').click()


The object is checked out now, and we're looking at the edit form:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/.../zuender/@@edit.html'
>>> browser.getLink('Metadata').click()
>>> browser.getControl(name='form.title').value
'Zuender'

Change the title:

>>> browser.getControl('Title').value = 'Feuerzeug'
>>> browser.getControl('Apply').click()
>>> 'There were errors' in browser.contents
False


Sorting 
-------

On the sorting tab the feed elements can be sorted via drag and drop. They can
also be pinned and hidden from the homepage. Open the politik.feed and check it
out:

>>> browser.open('/++skin++cms/repository/politik.feed')
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Sort').click()
>>> print browser.contents
<?xml ...
<table class="feedsorting">
  <thead>
    <tr>
      <th>
        Pinned
      </th>
      <th>
        Hidden on HP
      </th>
      <th>
      </th>
      <th>
        Author
      </th>
      <th>
        Title
      </th>
      <th>
        Position
      </th>
    </tr>
  </thead>
  <tbody>
  <tr>
    <td>
      ...<input type="checkbox" name="pin:list".../>
    </td>
    <td>
      ...<input ...name="hide..." ...type="checkbox".../>
    </td>
    <td>
      <img src="http://localhost/++skin++cms/@@/zeit-cms-repository-interfaces-IUnknownResource-zmi_icon.png" alt="UnknownResource" width="20" height="20" border="0" />
    </td>
    <td>
      None
    </td>
    <td>
      <a href="http://localhost/++skin++cms/repository/online/2007/01/rauchen-verbessert-die-welt">rauchen-verbessert-die-welt</a>
    </td>
    <td>
      1
    </td>
  </tr>
  </tbody>
</table>
...


Select the one entry we've syndicated for pinning:

>>> browser.getControl(name='pin:list').value = (
...     ['aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA=='])
>>> browser.getControl('Save').click()
>>> browser.getControl(name='pin:list').value
['aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==']

Now hide on hp:

>>> hide_ctl = browser.getControl(
...     name='hide.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4'
...          'tdmVyYmVzc2VydC1kaWUtd2VsdA==.')
>>> hide_ctl.value
False
>>> hide_ctl.value = True
>>> browser.getControl('Save').click()
>>> hide_ctl = browser.getControl(
...     name='hide.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4'
...          'tdmVyYmVzc2VydC1kaWUtd2VsdA==.')
>>> hide_ctl.value
True


Let's have a look at the source now:

>>> browser.getLink('Source').click()
>>> print browser.getControl('XML').value.replace('\r\n', '\n')
<feed xmlns="http://namespaces.zeit.de/CMS/feed">
  <title>Politik</title>
  <container>
    <block href="http://xml.zeit.de/online/2007/01/rauchen-verbessert-die-welt"
        pinned="true" hp_hide="true"/>
  </container>
</feed>

