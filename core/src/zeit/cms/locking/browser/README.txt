=======
Locking
=======

The lock icon shows information about the current lock[1]_:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Somalia')
>>> browser.getLink('Locks')
<Link text='[IMG] Locks' url="javascript:zeit.cms.lightbox_form('http://localhost:8080/++skin++cms/repository/online/2007/01/Somalia/@@locks.html')">


>>> browser.open('/++skin++cms/repository/online/2007/01/Somalia/@@locks.html')
>>> print browser.contents
<div>
  <h1>Locks</h1>
  ...
        <label for="form.locked">
          <span>Locked</span>
        </label>
        ...
        <div class="widget">False</div>
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
>>> print browser.contents
<div>
    ...
        <label for="form.locked">
          <span>Locked</span>
        </label>
        ...
        <div class="widget">True</div>
        ...
        <label for="form.locker">
          <span>Locker</span>
        </label>
        ...
        <div class="widget">zope.user</div>
      ...
    <input type="submit" id="form.actions.unlock" name="form.actions.unlock" value="Unlock" class="button" />
    ...
      


.. [1] For UI-Tests we need a Testbrowser:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


