=======
Locking
=======

The locks tab shows information about the current lock[1]_:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Somalia')
>>> browser.getLink('Locks').click()
>>> print browser.contents
<?xml ...
        <div id="actionsView">
          <span class="actionButtons">
            <input type="submit" id="form.actions.lock" name="form.actions.lock" value="Lock" class="button" />
          </span>
        </div>
        <div class="field-group">
          <fieldset>
            <legend></legend>
            <div>
      <div class="field   ">
        <label for="form.locked">
          <span>Locked</span>
        </label>
        <div class="hint"></div>
        <div class="widget">False</div>
      </div>
      <div class="field   ">
        <label for="form.locker">
          <span>Locker</span>
        </label>
        <div class="hint"></div>
        <div class="widget"></div>
      </div>
      <div class="field   ">
        <label for="form.locked_until">
          <span>Locked until</span>
        </label>
        <div class="hint"></div>
        <div class="widget"></div>
      </div>
            </div>
          </fieldset>
        </div>
        ...


When we lock we'll see the relevant information:

>>> browser.getControl('Lock').click()
>>> print browser.contents
<?xml ...
      <div class="field   ">
        <label for="form.locked">
          <span>Locked</span>
        </label>
        <div class="hint"></div>
        <div class="widget">True</div>
      </div>
      <div class="field   ">
        <label for="form.locker">
          <span>Locker</span>
        </label>
        <div class="hint"></div>
        <div class="widget">zope.user</div>
      </div>
      ...


.. [1] For UI-Tests we need a Testbrowser:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


