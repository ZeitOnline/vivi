================
Syndcation Views
================

Create a browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

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
<table>
  <thead>
    ...
    <th>
      Position
    </th>
    ...
  </thead>
  <tbody>
  </tbody>
</table>
...
  

The list is empty, because the user hasn't chosen any targets. Let's do that
now:

>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Als Ziel merken').click()

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


Feeds
=====

Let's create a new feed in the repository:

>>> browser.getLink('2006').click()
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
>>> browser.getLink('Metadaten').click()
>>> browser.getControl(name='form.title').value
'Zuender'

XXX test the read only view

