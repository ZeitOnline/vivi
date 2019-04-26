Purge
=====

Purge public caches via the HTTP *PURGE* method.

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zeit.purge.interfaces
>>> import zeit.cms.interfaces

Purge testcontent:

>>> content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
>>> purge = zeit.purge.interfaces.IPurge(content)
>>> purge.purge()
Purging Server1 http://www.zeit.de/testcontent
Purging Server2 http://www.zeit.de/testcontent

It is an error when a server returns anything but status "200":

>>> import zeit.purge.testing
>>> zeit.purge.testing.Server2.response = 404
>>> purge.purge()
Traceback (most recent call last):
    ...
PurgeError: [localhost:...] Got status 404 (Not Found)
>>> del zeit.purge.testing.Server2.response


Requests may not take longer than a certain time (which is configureable):

>>> zeit.purge.testing.Server1.need_time = zeit.purge.testing.timeout + 1
>>> purge.purge()
Traceback (most recent call last):
    ...
PurgeError: [localhost:...] timed out
>>> del zeit.purge.testing.Server1.need_time


Browser integration
-------------------

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')
>>> browser.open('http://localhost/++skin++cms/repository/testcontent')
>>> browser.getLink('Purge').click()
Purging Server1 http://www.zeit.de/testcontent
Purging Server2 http://www.zeit.de/testcontent
>>> print browser.contents
<...
   <li class="message">Purged http://xml.zeit.de/testcontent</li>
   ...

HTTP errors are displayed as an error message:

>>> zeit.purge.testing.Server2.response = 404
>>> browser.getLink('Purge').click()
Purging Server1 http://www.zeit.de/testcontent
Purging Server2 http://www.zeit.de/testcontent
>>> del zeit.purge.testing.Server2.response
>>> print browser.contents
<...
 <li class="error">Error while purging localhost:...: Got status 404 (Not Found)</li>
        ...
