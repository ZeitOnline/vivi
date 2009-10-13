Site control
============

The site control is situated in the sidebar:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')
>>> browser.handleErrors = False
>>> browser.open('http://localhost/++skin++vivi/repository')
>>> print browser.contents
<...
...<div class="panel unfolded" id="zeit-cms-sitecontrol">
  <h1>
    <a href="#">
        Site control
    </a>
  </h1>
  <div id="zeit.cms.sitecontrol.panelcontent" class="PanelContent">
  </div>
  <script type="text/javascript">
      ...
      var sidebar = new zeit.cms.sitecontrol.Sidebar(
        'http://localhost/++skin++vivi/repository/@@zeit.cms.sitecontrol');
        ...


The actual tree is loaded via javascript. The result is cached by the browser:

>>> browser.open(
...     'http://localhost/++skin++vivi/repository/@@zeit.cms.sitecontrol')
>>> print browser.headers
Status: 200 Ok
Cache-Control: public; max-age=360
Content-Length: ...
Content-Type: text/html;charset=utf-8
...


Currently there is nothing but the homepage in the dropdown because no
corresponding object could be found:

>>> print browser.contents
  <form action="#">
    <select name="site">
      <option class="homepage"
              value="http://localhost/++skin++vivi/repository/index">Homepage</option>
    </select>
    <input type="button" name="go" value="Open" />
  </form>


Create objects:

>>> import zeit.cms.repository.folder
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.testcontenttype.testcontenttype
>>> import zeit.cms.testing
>>> import zope.component
>>> zeit.cms.testing.set_site()
>>> repository = zope.component.getUtility(
... zeit.cms.repository.interfaces.IRepository)
>>> repository['deutschland'] = zeit.cms.repository.folder.Folder()
>>> repository['deutschland']['index'] = (
...     zeit.cms.testcontenttype.testcontenttype.TestContentType())
>>> repository['deutschland']['integration'] = zeit.cms.repository.folder.Folder()
>>> repository['deutschland']['datenschutz'] = zeit.cms.repository.folder.Folder()
>>> repository['wirtschaft'] = zeit.cms.repository.folder.Folder()

Now those objects which are created are listed. Note that there is an url to
deutschland/index and to deutschland/integration. So when there is an index it
will be directly addressed:

>>> browser.reload()
>>> print browser.contents
  <form action="#">
    <select name="site">
      <option class="homepage"
              value="http://localhost/++skin++vivi/repository/index">Homepage</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/index">Deutschland</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/datenschutz">Datenschutz</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/integration">Integration</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/wirtschaft">Wirtschaft</option>
    </select>
    ...


Additional sites
================

It is possible to register named ISitesProvider utilities to add further
objects to site control.

>>> sites = []
>>> class Sites(object):
...     def __iter__(self):
...         return (
...             zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/%s' % path)
...             for path in sites)
>>> sites_util = Sites()
>>> import zeit.cms.sitecontrol.interfaces
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerUtility(
...     sites_util, zeit.cms.sitecontrol.interfaces.ISitesProvider,
...     name='testsites')

Currently the utility doesn't return any result, thus nothing is added to the
site control:

>>> old_content = browser.contents
>>> browser.reload()
>>> browser.contents == old_content
True

When the utility spits out content it will be added. The css class corresponds
to the utility name:

>>> import zeit.cms.interfaces
>>> sites.append('testcontent')
>>> browser.reload()
>>> print browser.contents
  <form action="#">
    <select name="site">
      <option class="homepage"
              value="http://localhost/++skin++vivi/repository/index">Homepage</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/index">Deutschland</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/datenschutz">Datenschutz</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/integration">Integration</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/wirtschaft">Wirtschaft</option>
      <option class="testsites"
              value="http://localhost/++skin++vivi/repository/testcontent">testcontent</option>
    </select>
    ...

The testcontent does not have ressort or subresort. That's why it was put out
last. After assigning ressort it will be put after that ressort. The css class
indicates both ressort and testsites:

>>> import zeit.cms.checkout.helper
>>> with zeit.cms.testing.interaction():
...     with zeit.cms.checkout.helper.checked_out(
...     repository['testcontent']) as co:
...         co.ressort = u'Deutschland'
>>> browser.reload()
>>> print browser.contents
  <form action="#">
    <select name="site">
      <option class="homepage"
              value="http://localhost/++skin++vivi/repository/index">Homepage</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/index">Deutschland</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/datenschutz">Datenschutz</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/integration">Integration</option>
      <option class="ressort testsites"
              value="http://localhost/++skin++vivi/repository/testcontent">testcontent</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/wirtschaft">Wirtschaft</option>
    </select>
    ...


When also a subressort is assigned testcontent is sorted below the sub ressort:

>>> with zeit.cms.testing.interaction():
...     with zeit.cms.checkout.helper.checked_out(
...     repository['testcontent']) as co:
...         co.sub_ressort = u'Datenschutz'
>>> browser.reload()
>>> print browser.contents
  <form action="#">
    <select name="site">
      <option class="homepage"
              value="http://localhost/++skin++vivi/repository/index">Homepage</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/index">Deutschland</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/datenschutz">Datenschutz</option>
      <option class="sub_ressort testsites"
              value="http://localhost/++skin++vivi/repository/testcontent">testcontent</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/integration">Integration</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/wirtschaft">Wirtschaft</option>
    </select>
    ...



When a ressort/subressort is set which is not in the list the content is just
added last:

>>> with zeit.cms.testing.interaction():
...     with zeit.cms.checkout.helper.checked_out(
...         repository['testcontent']) as co:
...         co.ressort = u'Leben'
...         co.sub_ressort = None
>>> browser.reload()
>>> print browser.contents
  <form action="#">
    <select name="site">
      <option class="homepage"
              value="http://localhost/++skin++vivi/repository/index">Homepage</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/index">Deutschland</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/datenschutz">Datenschutz</option>
      <option class="sub_ressort"
              value="http://localhost/++skin++vivi/repository/deutschland/integration">Integration</option>
      <option class="ressort"
              value="http://localhost/++skin++vivi/repository/wirtschaft">Wirtschaft</option>
      <option class="testsites"
              value="http://localhost/++skin++vivi/repository/testcontent">testcontent</option>
    </select>
    ...


Cleanup

>>> gsm.unregisterUtility(
...     sites_util, zeit.cms.sitecontrol.interfaces.ISitesProvider,
...     name='testsites')
True
