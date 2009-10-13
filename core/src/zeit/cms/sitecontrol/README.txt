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
Cache-Control: private; max-age=360
Content-Length: ...
Content-Type: text/html;charset=utf-8
...
>>> print browser.contents
  <form action="#">
    <select name="site">
      <option value=""></option>
      <option class="ressort">Deutschland</option>
      <option class="sub_ressort"> Joschka Fisher</option>
      <option class="sub_ressort"> Datenschutz</option>
      <option class="sub_ressort"> Integration</option>
      <option class="sub_ressort"> Meinung</option>
      <option class="ressort">International</option>
      ...
