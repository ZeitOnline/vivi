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
    <a href="http://localhost/++skin++vivi/repository">
      Site control
    </a>
  </h1>
  <div id="zeit.cms.sitecontrol.panelcontent" class="PanelContent Tree">
  </div>
  <script type="text/javascript">
      ...
        var tree = new Tree('http://localhost/++skin++vivi/repository/zeit.cms.sitecontrol.tree', 'zeit.cms.sitecontrol.panelcontent');
        ...


The actual tree is loaded via javascript. The result is cached by the browser:

>>> browser.open(
...     'http://localhost/++skin++vivi/repository/zeit.cms.sitecontrol.tree')
>>> print browser.headers
Status: 200 Ok
Cache-Control: private; max-age=360
Content-Length: ...
Content-Type: text/html;charset=utf-8
...
>>> print browser.contents
  <ul>
      <li class="Root">
        <p>
        <a href="http://localhost/++skin++vivi/repository">Homepage</a>
        <span class="uniqueId">None</span>
        ...
