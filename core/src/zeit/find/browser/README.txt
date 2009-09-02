=========
Search UI
=========

For UI-Tests we need a Testbrowser and some setup[1]_:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


HTML views
==========

There is one main HTML view defined, which loads all the JavaScript and the
JSON template to setup the search UI. See the selenium tests for more details
on the UI itself:

>>> browser.open('http://localhost:8080/++skin++cms/find')
>>> print browser.contents
<html>
  <head>
    ...
    <script src="...json-template.js" type="text/javascript"> </script>
    <script src="...find.js" type="text/javascript"> </script>
    ...
    <script language="javascript">
            var application_url = 'http://localhost:8080/++skin++cms';
            var context_url = application_url;
    </script>
  </head>
  <body id="body">
    <div id="cp-search" class="zeit-find-search">
    </div>
    <script language="javascript">
     zeit.find.init_full_search();
    </script>
  </body>
</html>


The index of the CMS (ISite) is a search whyen using the vivi skin:

>>> browser.open('http://localhost:8080/++skin++vivi/')
>>> print browser.contents
<...
    var search = new zeit.find.Search(...
    ...


JSON views
==========

There are a number of views returning JSON data for the search UI.

Search form
-----------

The `search_form` view returns the template URL for the search form and the
data for dropdowns/selects:

>>> browser.open('http://localhost:8080/++skin++cms/search_form')
>>> browser.headers['Content-Type']
'text/json'
>>> import cjson
>>> import pprint
>>> pprint.pprint(cjson.decode(browser.contents))
{'ressorts': [{'ressort': 'Deutschland'},...
 'template_url': 'http://localhost:8080/++skin++cms/@@/zeit.find/search_form.jsont',
 'types': [{'title': 'Channel', 'type': 'channel'},
           {'title': 'File', 'type': 'file'},
           {'title': 'Folder', 'type': 'collection'}...

    


Favorites
---------

There is a JSON which, which toggles the favorites status of a content object.

The favorites are stored inside the clipboard in a special clip named
"Favoriten". If the principal never added favorites before, the clip does not
exist:

>>> import zeit.cms.clipboard.interfaces 
>>> clipboard = zeit.cms.clipboard.interfaces.IClipboard(principal)
>>> clipboard["Favoriten"]
Traceback (most recent call last):
...
KeyError: 'Favoriten'

Adding a content object as a favorite requires the call of the
`toggle_favorited` view with the uniqueId of the object:

>>> browser.open('http://localhost:8080/++skin++cms/toggle_favorited?uniqueId=http://xml.zeit.de/online/2007/01/Somalia')

It returns the css class for the favorite star:

>>> pprint.pprint(cjson.decode(browser.contents))
{'favorited_css_class': 'toggle_favorited favorited',...

The clipboard now has a clip "Favoriten" with one entry:

>>> clipboard["Favoriten"].keys()
[u'Somalia']

The favorites tab now lists the favorited object:

>>> browser.open('http://localhost:8080/++skin++cms/favorites')
>>> pprint.pprint(cjson.decode(browser.contents))
{'results': [{...
    'favorite_url': 'http://localhost:8080/++skin++cms/toggle_favorited?uniqueId=http://xml.zeit.de/online/2007/01/Somalia',
    'favorited': True,
    'favorited_css_class': 'toggle_favorited favorited',
    ...
 'template_url': 'http://localhost:8080/++skin++cms/@@/zeit.find/search_result.jsont'}


The view does not break when there is a clip in the favorites. The clip isn't
shown though:

>>> import zeit.cms.clipboard.entry
>>> clipboard['Favoriten']['Clip'] = zeit.cms.clipboard.entry.Clip('Clip')
>>> browser.open('http://localhost:8080/++skin++cms/favorites')
>>> result = cjson.decode(browser.contents)
>>> len(result['results'])
1
>>> del clipboard['Favoriten']['Clip']



Calling the toggle view again removes the object from the favorites:

>>> browser.open('http://localhost:8080/++skin++cms/toggle_favorited?uniqueId=http://xml.zeit.de/online/2007/01/Somalia')
>>> pprint.pprint(cjson.decode(browser.contents))
{'favorited_css_class': 'toggle_favorited not_favorited',...

The clip persists, but is now empty:

>>> clipboard["Favoriten"].keys()
[]

 

Footnotes
=========

.. [1] Setup

    We need to set the site since we're a functional test:

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()

    We also need an interaction as we needs to get the principal:

    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'zope.user')
    >>> participation = zope.security.testing.Participation(principal)
