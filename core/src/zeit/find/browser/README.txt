=========
Search UI
=========

For UI-Tests we need a Testbrowser and some setup:


>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

>>> import zope.security.testing
>>> principal = zope.security.testing.Principal(u'zope.user')
>>> participation = zope.security.testing.Participation(principal)

>>> import zeit.cms.testing
>>> browser = zeit.cms.testing.Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')


HTML views
==========

There is one main HTML view defined, which loads all the JavaScript and the
JSON template to setup the search UI. See the selenium tests for more details
on the UI itself:

>>> browser.open('http://localhost:8080/++skin++cms/find')
>>> print(browser.contents)
<html>
  ...
  <body>
    <div id="cp-search" class="zeit-find-search">
    </div>
    <script language="javascript">
     zeit.find.init_full_search();
    </script>
  </body>
</html>


The index of the CMS (ISite) is a search whyen using the vivi skin:

>>> browser.open('http://localhost:8080/++skin++vivi/')
>>> print(browser.contents)
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
>>> print(browser.headers)
Status: 200 Ok
Content-Length: ...
Content-Type: text/json...

>>> import json
>>> import pprint
>>> pprint.pprint(json.loads(browser.contents))
{u'access': [{u'access': u'free', u'access_title': u'frei verf\xfcgbar'},...
 u'products': [{u'product_id': u'ZEI', u'product_name': u'Die Zeit'},...
 u'ressorts': [{u'ressort': u'Deutschland', u'ressort_name': u'Deutschland'},...
 u'series': [{u'serie': u'-', u'serie_title': u'-'},...
 u'template_url': u'http://localhost:8080/++skin++cms/fanstatic/zeit.find/search_form.jsont',
 u'types': [{u'title': u'Image Group', u'type': u'image-group'}]}


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

>>> browser.open(
...     'http://localhost:8080/++skin++cms/toggle_favorited?'
...     'uniqueId=http://xml.zeit.de/online/2007/01/Somalia')
>>> browser.open(
...     'http://localhost:8080/++skin++cms/toggle_favorited?'
...     'uniqueId=http://xml.zeit.de/2006/DSC00109_2.JPG')

It returns the css class for the favorite star:

>>> pprint.pprint(json.loads(browser.contents))
{u'favorited_css_class': u'toggle_favorited favorited',...

The clipboard now has a clip "Favoriten" with one entry:

>>> clipboard["Favoriten"].keys()
[u'Somalia', u'DSC00109_2.JPG']


Calling the toggle view again removes the object from the favorites:

>>> browser.open(
...     'http://localhost:8080/++skin++cms/toggle_favorited?'
...     'uniqueId=http://xml.zeit.de/online/2007/01/Somalia')
>>> browser.open(
...     'http://localhost:8080/++skin++cms/toggle_favorited?'
...     'uniqueId=http://xml.zeit.de/2006/DSC00109_2.JPG')
>>> pprint.pprint(json.loads(browser.contents))
{u'favorited_css_class': u'toggle_favorited not_favorited',...

The clip persists, but is now empty:

>>> clipboard["Favoriten"].keys()
[]


Search
======

The search view returns all data for rendering the result:

>>> import zeit.find.testing
>>> zeit.find.testing.LAYER.set_result('zeit.find.tests', 'data/obama.json')
>>> browser.open('/++skin++cms/search_result?title=Obama')
>>> result = json.loads(browser.contents)
>>> pprint.pprint(result)
{u'results': [{u'application_url': u'http://localhost:8080/++skin++cms',
              ...
              u'graphical_preview_url': u'http://localhost:8080/++skin++cms/repository/.../thumbnail',
             ...
 u'template_url': u'http://localhost:8080/++skin++cms/++noop++a12dffa9629480a5cafd9df8a674891e/fanstatic/zeit.find/search_result.jsont'}

Favorites are marked in the search result as well:

>>> first_result = result['results'][0]
>>> pprint.pprint(first_result)
{...
 u'favorite_url': u'http://localhost:8080/++skin++cms/toggle_favorited?uniqueId=http://xml.zeit.de/online/2007/01/Somalia',
 u'favorited': False,
 u'favorited_css_class': u'toggle_favorited not_favorited',
 ...

Toggle favorite and search again:

>>> browser.open(first_result['favorite_url'])
>>> browser.open('/++skin++cms/search_result?fulltext=Obama')
>>> result = json.loads(browser.contents)
>>> first_result = result['results'][0]
>>> pprint.pprint(first_result)
{...
 u'favorite_url': u'http://localhost:8080/++skin++cms/toggle_favorited?uniqueId=http://xml.zeit.de/online/2007/01/Somalia',
 u'favorited': True,
 u'favorited_css_class': u'toggle_favorited favorited',
 ...

This also works if there is a Clip in the favorites:

>>> clipboard['Favoriten']['Clip'] = zeit.cms.clipboard.entry.Clip('Clip')
>>> browser.open('/++skin++cms/search_result?fulltext=Obama')
>>> result = json.loads(browser.contents)
>>> first_result = result['results'][0]
>>> pprint.pprint(first_result)
{...
 u'favorite_url': u'http://localhost:8080/++skin++cms/toggle_favorited?uniqueId=http://xml.zeit.de/online/2007/01/Somalia',
 u'favorited': True,
 u'favorited_css_class': u'toggle_favorited favorited',
 ...

The last query parameters are available:

>>> browser.open('/++skin++cms/zeit.find.last-query')
>>> result = json.loads(browser.contents)
>>> pprint.pprint(result)
{...
 u'fulltext': u'Obama',
 ...
 u'types:list': [],
 ...
