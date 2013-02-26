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
>>> print browser.contents
<?xml ...
    <li class="message">"politik.feed" has been added to your syndication
    targets.</li>
    ...

Visit the syndication page again:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> link = browser.getLink('Syndicate').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html...
<table...
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
        ...lock-open...
      </td>
      <td>
        Politik
      </td>
      <td>
        <a href="...">...politik.feed</a>
      </td>
      <td>
      </td>
      <td>
        <a ...target="_blank" ...>Preview</a>
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
    <li class="message">"rauchen-verbessert-die-welt" has been syndicated to
    politik.feed</li>...
<table...
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
        ...lock-open...
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
      <td>
        <a ...>Preview</a>
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


Locking indicator
-----------------

Locking information is also be displayed in the syndication manager:

>>> browser.open('http://localhost/++skin++cms/repository/wirtschaft.feed')
>>> browser.getLink("Checkout").click()
>>> browser.getLink("Remember as syndication target").click()
>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> browser.getLink('Syndicate').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html...
<div id="edit-form">
<h1> Syndicate "rauchen-verbessert-die-welt" </h1>
<form method="POST">
  ...
    <tr>
      <td>
        <input .../>
      </td>
      <td>
        ...lock-closed-mylock...
      </td>
      <td>
        Wirtschaft
      </td>
      <td>
        <a href="...">...wirtschaft.feed</a>
      </td>
      <td>
      </td>
      <td>
        <a ...>Preview</a>
      </td>
...


When we try to syndicate to that feed we'll get an error message:

>>> wirtschaft_checkbox = browser.getControl(
...  name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3dpcnRzY2hhZnQuZmVlZA==.')
>>> wirtschaft_checkbox.value = True
>>> browser.getControl('Syndicate').click()
>>> print browser.contents
<?xml ...
        <li class="error">Could not syndicate because
            "http://xml.zeit.de/wirtschaft.feed" could not be locked or
            checked out.</li>
    ...

Preview
-------

There is also a preview link, to be able to preview the feed:

>>> bookmark = browser.url
>>> import zeit.cms.testing
>>> zeit.cms.testing.click_wo_redirect(browser, 'Preview', index=1)
HTTP Error 303: See Other
http://localhost/preview-prefix/politik.feed

Note that if there is an `index` object in the container the preview url is
*not* the url of the feed itself, but the `index` of the container of the feed.
Create an index:

>>> browser.open('http://localhost/++skin++cms/repository')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Folder']
>>> browser.open(menu.value[0])
>>> browser.getControl('File name').value = 'index'
>>> browser.getControl('Add').click()

The preview goes to the index now:

>>> browser.open(bookmark)
>>> zeit.cms.testing.click_wo_redirect(browser, 'Preview', index=1)
HTTP Error 303: See Other
http://localhost/preview-prefix/index


Syndicating without showing it on the homepage
----------------------------------------------

A very common case is that a content should be published but not be visible on
the homepage. This is a separate action:

>>> browser.open(bookmark)
>>> politik_checkbox = browser.getControl(
...    name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> politik_checkbox.value = True
>>> browser.getControl('Synd. w/o HP').click()
>>> print browser.contents
<?xml ...
    ..."rauchen-verbessert-die-welt" has been syndicated to politik.feed...

Go to politk.feed to see that it is hidden on the HP:

>>> browser.getLink('politik').click()
>>> hp_checkbox = browser.getControl(name='hp.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==.')
>>> hp_checkbox.value
False

When we syndicate again *with* HP, the flag is set again:

>>> browser.open(bookmark)
>>> politik_checkbox = browser.getControl(
...    name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> politik_checkbox.value = True
>>> browser.getControl('Syndicate').click()
>>> print browser.contents
<?xml ...
    ..."rauchen-verbessert-die-welt" has been syndicated to politik.feed...
>>> browser.getLink('politik').click()
>>> hp_checkbox = browser.getControl(name='hp.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==.')
>>> hp_checkbox.value
True


Syndicating without relateds
----------------------------

A very common case is that a content should be syndicated without relateds.
This is a separate action:

>>> browser.open(bookmark)
>>> politik_checkbox = browser.getControl(
...    name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> politik_checkbox.value = True
>>> browser.getControl('Synd. w/o relateds').click()
>>> print browser.contents
<?xml ...
    ..."rauchen-verbessert-die-welt" has been syndicated to politik.feed...

Go to politk.feed to see that it is w/o related:

>>> browser.getLink('politik').click()
>>> relateds_checkbox = browser.getControl(name='visible_relateds.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==.')
>>> relateds_checkbox.value
False

When we syndicate again *with* relateds, the flag is set again:

>>> browser.open(bookmark)
>>> politik_checkbox = browser.getControl(
...    name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> politik_checkbox.value = True
>>> browser.getControl('Syndicate').click()
>>> print browser.contents
<?xml ...
    ..."rauchen-verbessert-die-welt" has been syndicated to politik.feed...
>>> browser.getLink('politik').click()
>>> relateds_checkbox = browser.getControl(name='visible_relateds.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==.')
>>> relateds_checkbox.value
True

Publishing
----------

In the syndication tab it is very handy to publish the feeds right away.
Publish the politik channel:

>>> browser.open(bookmark)
>>> politik_checkbox = browser.getControl(
...    name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> politik_checkbox.value = True
>>> browser.getControl('Publish').click()
>>> print browser.contents
<?xml ...
        <li class="error">Could not publish "politik.feed".</li>
        ...

Make the object publishable and try again:

>>> import zeit.cms.workflow.mock
>>> feed_id = 'http://xml.zeit.de/politik.feed'
>>> zeit.cms.workflow.mock._can_publish[feed_id] = True
>>> browser.getControl('Publish').click()
Publishing: http://xml.zeit.de/politik.feed


Feeds
=====

Let's create a new feed in the repository:

>>> browser.open('http://localhost/++skin++cms/repository/2006')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Feed']
>>> browser.open(menu.value[0])

We are looking at the add form now. Fill in the title and add the feed:

>>> browser.getControl('Title').value = 'Zuender'
>>> browser.getControl('File name').value = 'zuender'
>>> browser.getControl('Limit amount').value = '20'
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
also be pinned and hidden from the homepage. Open the politik.feed and first
have a look at its display view:

>>> browser.open('/++skin++cms/repository/politik.feed')
>>> print browser.title.strip()
Politik – Feed contents
>>> print browser.contents
<?xml ...
<table class="feedsorting table-sorter">
  <thead>
    <tr>
      <th>
        #
      </th>
      <th>
        Pinned
      </th>
      <th>
        HP
      </th>
      <th>
        Big
      </th>
      <th>
        Relateds
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
        Hits
      </th>
    </tr>
  </thead>
  ...

The checkboxes are not clickable:

>>> browser.getControl(name='pin:list').disabled
True


Check it out to change the order. We're at the edit/sort page after checking out:

>>> browser.getLink('Checkout').click()
>>> print browser.title.strip()
Politik – Edit feed contents
>>> print browser.contents
<?xml ...
<table class="feedsorting table-sorter">
  <thead>
    <tr>
      <th>
        #
      </th>
      <th>
        Remove
      </th>
      <th>
        Pinned
      </th>
      <th>
        HP
      </th>
      <th>
        Big
      </th>
      <th>
        Relateds
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
        Hits
      </th>
    </tr>
  </thead>
  <tbody>
  <tr>
    <td>
      1
    </td>
    ...
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
    </td>
  </tr>
  </tbody>
</table>
...

Note that there is no "Contents" tab after checkout:

>>> browser.getLink('Contents')
Traceback (most recent call last):
    ...
LinkNotFoundError

Select the one entry we've syndicated for pinning:

>>> browser.getControl(name='pin:list').value = (
...     ['aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA=='])
>>> browser.getControl('Save').click()
>>> browser.getControl(name='pin:list').value
['aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==']

Now hide on hp:

>>> hide_ctl = browser.getControl(
...     name='hp.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4'
...          'tdmVyYmVzc2VydC1kaWUtd2VsdA==.')
>>> hide_ctl.value
True
>>> hide_ctl.value = False
>>> browser.getControl('Save').click()
>>> hide_ctl = browser.getControl(
...     name='hp.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4'
...          'tdmVyYmVzc2VydC1kaWUtd2VsdA==.')
>>> hide_ctl.value
False


Let's have a look at the source now:

>>> browser.getLink('Source').click()
>>> print browser.getControl('XML').value.replace('\r\n', '\n')
<channel> 
  <title>Politik</title>
  <container>
    <block ...
           href="http://xml.zeit.de/online/2007/01/rauchen-verbessert-die-welt"...
           hidden_relateds="false"
           hp_hide="true"
           pinned="true"/>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype">50</object_limit>
</channel>


Big layout
----------

To make a "big" layout the correponding checkbox can be clicked:

>>> browser.getLink('Edit contents').click()
>>> browser.getControl(name="layout.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==."
...     ).value = True
>>> browser.getControl('Save').click()
>>> browser.getControl(name="layout.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==."
...     ).value
True

Its also indicated in the source:

>>> browser.getLink('Source').click()
>>> print browser.getControl('XML').value.replace('\r\n', '\n')
<channel> 
  <title>Politik</title>
  <container>
    <block ...
           href="http://xml.zeit.de/online/2007/01/rauchen-verbessert-die-welt"...
           hidden_relateds="false"
           hp_hide="true"
           pinned="true"
           layout="big"/>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype">50</object_limit>
</channel>

Hidden relateds
---------------

There is a checkbox to hide the relateds:

>>> browser.getLink('Edit contents').click()
>>> browser.getControl(name="visible_relateds.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==."
...     ).value = False
>>> browser.getControl('Save').click()
>>> browser.getControl(name="visible_relateds.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==."
...     ).value
False

Its also indicated in the source:

>>> browser.getLink('Source').click()
>>> print browser.getControl('XML').value.replace('\r\n', '\n'),
<channel> 
  <title>Politik</title>
  <container>
    <block ...
           href="http://xml.zeit.de/online/2007/01/rauchen-verbessert-die-welt"...
           hidden_relateds="true"
           hp_hide="true"
           pinned="true"
           layout="big"/>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype">50</object_limit>
</channel>

Removing items from channels
----------------------------

Items can be removed at the contents page:

>>> browser.getLink('Edit contents').click()
>>> browser.getControl(name='remove.aHR0cDovL3htbC56ZWl0LmRlL29ubGluZS8yMDA3LzAxL3JhdWNoZW4tdmVyYmVzc2VydC1kaWUtd2VsdA==.').value = True
>>> browser.getControl('Save').click()

Let's have a look at the source now:

>>> browser.getLink('Source').click()
>>> print browser.getControl('XML').value.replace('\r\n', '\n')
<channel> 
  <title>Politik</title>
  <container/>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype">50</object_limit>
</channel>


Removing feeds from the syndication targets list
------------------------------------------------

The 'Politik' Feed is currently a syndication target:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> link = browser.getLink('Syndicate').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html...
</tr>
</thead>
<tbody>
  <tr>
    <td>
      <input ...  />
    </td>
    <td>
        ...lock-closed-mylock...
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
    <td>
      <a ...target="_blank"...>Preview</a>
    </td>
</tr>
...


We remove it now from the syndication targets:

>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Remove from my syndication targets').click()
>>> print browser.contents
<?xml ...
    <li class="message">"politik.feed" has been removed from your syndication targets.</li>
...



External urls in href
---------------------

When there are external url in the href we generate a fake object.  Make sure
we can see it in the UI:

>>> browser.getLink('Politik').click()
>>> browser.getLink('Source').click()
>>> browser.getControl('XML').value = '''\
... <channel>
...   <title>Politik</title>
...   <container>
...     <block layout="" priority="" href="http://www.zeit.de/news/artikel/2008/04/22/2517661.xml" id="" sticky="">
...         <supertitle>Schmiergeldaffäre</supertitle>
...         <title>Samsung-Chef Lee tritt zurück</title>
...         <text>Der mächtigste Geschäftsmann Südkoreas, Lee Kun Hee, zieht sich von seinem Posten zurück. Der Chef des Samsung-Konzerns ist wegen Steuerhinterziehung angeklagt. Ihm drohen mehrere Jahre Haft.</text>
...         <byline/>
...         <short>
...             <title>Schmiergeldaffäre</title>
...             <text>Samsung-Chef Lee tritt zurück</text>
...         </short>
...         <related>
...             <block href="cms:/cms/work/online/2008/16/bahn-spd-kommentar" pos="1">
...                 <title>Bahnprivatisierung</title>
...                 <text>SPD-Chef Beck beweist Führungsstärke</text>
...             </block>
...         </related>
...     </block>
...   </container>
...   <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype">50</object_limit>
... </channel>'''

>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
    ...Updated on...
>>> browser.getLink('Edit contents').click()
>>> print browser.contents
<?xml ...
    <td>
      1
    </td>
    ...
    <td>
      <a href="http://www.zeit.de/news/artikel/2008/04/22/2517661.xml">Samsung-Chef Lee tritt zurück</a>
    </td>
    ...



Bug hunting
===========

People do strange things and add the channel to itself. Let's try that:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...              'wirtschaft.feed/edit.html')
>>> browser.getLink('Checkin').click()
>>> browser.getLink('Syndicate').click()
>>> browser.getControl(
...     name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3dpcnRzY2hhZnQuZmVlZA==.'
...     ).value = True
>>> browser.getControl('Syndicate').click()

Let's have a look at the feed now:

>>> browser.open('http://localhost/++skin++cms/repository/wirtschaft.feed')
>>> print browser.contents
<?xml ...
    <td>
      1
    </td>
    ...
    <td>
      <a href="http://localhost/++skin++cms/repository/wirtschaft.feed">Wirtschaft</a>
    </td>
    ...


Let's remove the title of the feed to make sure we don't puke. Note that there
is now way to remove the title w/o editing the source:

>>> browser.getLink('Checkout').click()
>>> browser.getLink('Source').click()
>>> browser.getControl('XML').value = '''\
... <channel>
...   <container>
...     <block xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" href="http://xml.zeit.de/wirtschaft.feed">
...       <references/>
...     </block>
...     <block href="http://xml.zeit.de/online/2007/01/Querdax">
...       <teaser xmlns="http://xml.zeit.de/CMS/Teaser">
...         <title/>
...         <text/>
...       </teaser>
...     </block>
...     <block href="http://xml.zeit.de/online/2007/01/Rosia-Montana">
...       <teaser xmlns="http://xml.zeit.de/CMS/Teaser">
...         <title/>
...         <text/>
...       </teaser>
...     </block>
...     <block href="http://xml.zeit.de/online/2007/01/Flugsicherheit">
...       <teaser xmlns="http://xml.zeit.de/CMS/Teaser">
...         <title/>
...         <text/>
...       </teaser>
...     </block>
...   </container>
...   <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype">50</object_limit>
... </channel>'''
>>> browser.getControl('Apply').click()
>>> browser.getLink('Checkin').click()
>>> browser.getLink('Contents').click()
>>> print browser.contents
<?xml ...
    <td>
      1
    </td>
    ...
    <td>
      <a href="http://localhost/++skin++cms/repository/wirtschaft.feed">wirtschaft.feed</a>
    </td>
    ...
