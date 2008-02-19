=============
Zeit Workflow
=============

The workflow is state oriented. There are several states which all can be set
using the workflow tab[1]_:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Somalia')
>>> browser.getLink('Workflow').click()

States
======

The states are explained below.

Bearbeitet (Redaktion)
+++++++++++++++++++++++

This state tells if the editors have finished their work. The initlal value is
"no":

>>> browser.getControl('Bearbeitet').displayValue
['no']

The available options are as follows:

>>> browser.getControl('Bearbeitet').displayOptions
['no', 'yes', 'not necessary']


Korrigiert 
++++++++++

Korrigiert states if the Korrektor is done. The state has the same values as
**Bearbeitet**:

>>> browser.getControl('Korrigiert').displayValue
['no']
>>> browser.getControl('Korrigiert').displayOptions
['no', 'yes', 'not necessary']

Veredelt
++++++++

Veredelt states if Links etc. were added to the document. The state has the
same values as **Bearbeitet**:

>>> browser.getControl('Veredelt').displayValue
['no']
>>> browser.getControl('Veredelt').displayOptions
['no', 'yes', 'not necessary']


Bilder hinzugefügt
++++++++++++++++++

The graphics department adds image. The state has the same values as
**Bearbeitet**:

>>> browser.getControl('Bilder hinzugefügt').displayValue
['no']
>>> browser.getControl('Bilder hinzugefügt').displayOptions
['no', 'yes', 'not necessary']


Eilmeldung
++++++++++

Checking the Eilmeldung box makes the dockument public even though it was not
corrected etc:

>>> browser.getControl('Eilmeldung').selected
False



Veröffentlichungszeitraum
+++++++++++++++++++++++++

An object is only visible to public during the timespan given. Leaving the
fields empty means no restriction. This is also the default:

>>> browser.getControl('Von').value
''
>>> browser.getControl('Bis').value
''


Transitions
===========

There are no explicit transitions defined. Instead every state attribute can
currently be set to any value at will. Let's say our document is edited:

>>> browser.getControl('Bearbeitet').displayValue = ['yes']
>>> browser.getControl('Apply').click()
>>> browser.getControl('Bearbeitet').displayValue
['yes']


When we publish a document we set the "published" field:

>>> browser.getControl('Published').selected = True
>>> browser.getControl('Apply').click()
>>> browser.getControl('Published').selected
True



Automatic workflow properties
=============================

There are some properties which are set automatically on various occasions.

Date first released
+++++++++++++++++++

The "date first released" is the date when the object was first published.

>>> print browser.contents
<?xml ...
        <label for="form.last_modified_by">
          <span>Last modified by</span>
        </label>
        <div class="hint"></div>
        <div class="widget">Nothing</div>
        ...
        <label for="form.date_first_released">
          <span>Date first released</span>
        </label>
        <div class="hint"></div>
        <div class="widget"><span class="dateTime">2008 2 12  07:41:20 </span></div>
        ...

The published date is already set.

The "last modified by" property is set on checkin. Check the object out and in
again:

>>> browser.getLink('Checkout').click()
>>> browser.handleErrors = False
>>> browser.getLink('Checkin').click()
>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        <label for="form.last_modified_by">
          <span>Last modified by</span>
        </label>
        <div class="hint"></div>
        <div class="widget">User</div>
        ...
        <label for="form.date_first_released">
          <span>Date first released</span>
        </label>
        <div class="hint"></div>
        <div class="widget"><span class="dateTime">2008 2 12  07:41:20 </span></div>
        ...



Locks
=====

The locks tab shows information about the current lock:

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

