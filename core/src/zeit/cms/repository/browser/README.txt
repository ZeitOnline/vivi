========
ZEIT CMS
========

Create a browser first::

  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> browser = ExtendedTestBrowser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


File Listing
============

The filelisting is to be found under /repository. Open it::

  >>> browser.open('http://localhost/++skin++cms/repository')

To dive into folder objects we use a Javascript based tree. The testbrowser
doesn't support Javascript unforunately. Therefore we're just opening the url::
  
    >>> browser.open(
    ...     'http://localhost/++skin++cms/repository/online/2007/01')
    >>> print browser.contents
    <?xml version...
    <!DOCTYPE ...
    ...Querdax...
    ...Saarland...
    ...Saddam...

