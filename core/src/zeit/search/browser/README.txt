=========
Search UI
=========

Create a test browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


The search form is located in the side bar.

>>> browser.open('http://localhost/++skin++cms/')
>>> print browser.contents
<?xml ...
<div class="panel unfolded" id="SearchPanel">
 <h1>...Suche...</h1>
 <div class="PanelContent Search">
    <form id="search-form"
          action="http://localhost/++skin++cms/search.html"
          class="hide-extended">
      <input type="text" name="search.text" id="search.text" />
    ...
    </form>
  </div>
    ...


Note that in the test we only can search for "linux", so we do that:

>>> browser.getControl(name="search.text").value = 'linux'
>>> browser.getControl('Suchen').click()
>>> print browser.contents
<?xml ...
    <title> Suche </title>
    ...
<table class="contentListing">
  <thead>
    <tr>
      <th>...Autor...</th>
      <th>...Titel...</th>
      <th>...Jahr/Vol...</th>
      <th>...Seite...</th>
      <th>...</th>
    </tr>
  </thead>
  <tbody>
    <tr class="odd">
      <td>
        ...
      </td>
      ...


Note that after the search the search term is still filled in the search box:

>>> browser.getControl(name='search.text', index=0).value
'linux'

Even when we navigate somewhere else, it's filled in:

>>> browser.getLink('Dateiverwaltung').click()
>>> browser.getControl(name='search.text').value
'linux'
