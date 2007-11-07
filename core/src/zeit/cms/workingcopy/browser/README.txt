============
Working Copy
============

The working copy is the area of the CMS where users actually edit content.
Create a test browser first::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


When we access our working copy it is created on the fly if it does not exist
yet. So let's open our workingcopy. It doesn't contain any documents, yet::

  >>> browser.open('http://localhost/++skin++cms/workingcopy/zope.mgr')
  >>> print browser.contents
  <?xml version...
  <!DOCTYPE ...
  Keine ausgecheckten Dokumente...

 
Adding content to the working copy works by checking them out. Let's view the
repository and checkout a document::

  >>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia')
  >>> print browser.contents
  <?xml version...
  <!DOCTYPE ...
  ...namespaces.zeit.de...
  ...Terrorismus...
  ...Jochen Stahnke...

Checkout the Somalia Article::

  >>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia/checkout')

Checking out redirected us to the document *in* the working copy::

  >>> browser.url
  'http://localhost/++skin++cms/workingcopy/zope.mgr/Somalia/@@view.html'


Looking at our working copy also shows the `Somalia` article::

  >>> browser.open('http://localhost/++skin++cms/workingcopy/zope.mgr')
  >>> print browser.contents
  <?xml version...
  <!DOCTYPE ...
  ...Somalia...
