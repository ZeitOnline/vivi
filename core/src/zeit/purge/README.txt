Purge
=====

Purge public caches.

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zeit.purge.interfaces
>>> import zeit.cms.interfaces

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
HTTPException: Server localhost:... returned status 404 (Not Found)
>>> del zeit.purge.testing.Server2.response


Requests may not take longer than a certain time (which is configureable):

>>> zeit.purge.testing.Server1.need_time = zeit.purge.testing.timeout + 1
>>> purge.purge()
Traceback (most recent call last):
    ...
timeout: timed out
>>> del zeit.purge.testing.Server1.need_time
