=======
Locking
=======

The lock icon shows information about the current lock:

>>> from zeit.cms.testing import Browser
>>> browser = Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')
>>> url = ('http://localhost:8080/++skin++cms/repository/online'
...        '/2007/01/Somalia')
>>> browser.open(url)
>>> browser.getLink('Manage lock')
<Link text='Manage lock' url='javascript:zeit.cms.lightbox_form('http://localhost:8080/++skin++cms/repository/online/2007/01/Somalia/@@locks.html')'>
>>> print(browser.contents)
<?xml...
    <img src=".../lock-open.png" title="Not locked" class="lock-open" />
    ...


Open the lightbox. The object is currently not locked:

>>> browser.open(url + '/@@locks.html')
>>> print(browser.contents)
<div>
  <h1>Locks</h1>
  ...
        <label for="form.locked">
          <span>Locked</span>
        </label>
        ...<input class="checkboxType" id="...
        ...
        <label for="form.locker">
          <span>Locker</span>
        </label>
        ...
        <div class="widget"></div>
        ...
        <label for="form.locked_until">
          <span>Locked until</span>
        </label>
        ...
        <div class="widget"></div>
        ...
  <div class="form-controls">
    <input type="submit" id="form.actions.lock" name="form.actions.lock" value="Lock" class="button" />
  </div>
  ...



When we lock we'll see the relevant information:

>>> browser.getControl('Lock').click()
>>> print(browser.contents)
<div>
    ...
        <label for="form.locked">
          <span>Locked</span>
        </label>
        ...<input class="checkboxType" checked="checked" ...
        ...
        <label for="form.locker">
          <span>Locker</span>
        </label>
        ...
        <div class="widget">zope.user</div>
      ...
    <input type="submit" id="form.actions.unlock" name="form.actions.unlock" value="Unlock" class="button" />
    ...


Make sure a lock message was send to the user:

>>> browser.open(url)
>>> print(browser.contents)
<?xml ...
    <li class="message">"Somalia" has been locked.</li>
    ...
    <img src=".../lock-closed-mylock.png" title="Locked by you"
        class="lock-closed-mylock" />
    ...

We can now unlock Somalia:

>>> browser.getLink('Manage lock')
<Link text='Manage lock' url='javascript:zeit.cms.lightbox_form('http://localhost:8080/++skin++cms/repository/online/2007/01/Somalia/@@locks.html')'>
>>> browser.open(url + '/@@locks.html')
>>> browser.getControl('Unlock').click()
>>> print(browser.contents)
<div>
  <h1>Locks</h1>
  ...
        <label for="form.locked">
          <span>Locked</span>
        </label>
        ...<input class="checkboxType" id="...
        ...

Make sure the unlock message was sent to the user:

>>> browser.open(url)
>>> print(browser.contents)
<?xml ...
    <li class="message">"Somalia" has been unlocked.</li>
    ...


Let's lock the object again to test stealing:

>>> browser.open(url + '/@@locks.html')
>>> browser.getControl('Lock').click()
>>> print(browser.contents)
<div>
    ...
        <label for="form.locked">
          <span>Locked</span>
        </label>
        ...<input class="checkboxType" checked="checked"...


Login in as zmgr and steal the lock:

>>> mgr = Browser(layer['wsgi_app'])
>>> mgr.login('zmgr', 'mgrpw')
>>> mgr.open(url)
>>> print(mgr.contents)
<?xml ...
    <img src=".../lock-closed.png" title="Locked by zope.user"
        class="lock-closed" />...
>>> mgr.open(url + '/@@locks.html')
>>> mgr.getControl('Steal lock').click()
>>> print(mgr.contents)
<div>
    ...
        <label for="form.locked">
          <span>Locked</span>
        </label>
        ...<input class="checkboxType" checked="checked"...
        <label for="form.locker">
          <span>Locker</span>
        </label>
        ...
        <div class="widget">zope.mgr</div>
        ...


Make sure the unlock message was sent to the user:

>>> mgr.open(url)
>>> print(mgr.contents)
<?xml ...
    <li class="message">The lock on "Somalia" has been stolen from
        "zope.user".</li>
    ...
