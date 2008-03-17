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
>>> browser.getControl('Save state').click()
>>> browser.getControl('Bearbeitet').displayValue
['yes']


To publish the document, hit the 'publish' button:

>>> browser.handleErrors = False
>>> browser.getControl("publish").click()


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
      <div class="field   ">
        <label for="form.date_last_modified">
          <span>Date last modified</span>
        </label>
        <div class="hint"></div>
        <div class="widget"><span class="dateTime">2008 3 7  12:47:16 </span></div>
        ...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
        <div class="widget">True</div>
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



Publishing checked out resources
================================

There are a view race conditions regarding webdav properties. We concider the
workflow properties "live" i.e. they are only supposed to exist on the server.
When an object is checked out, all properties are copied so they can be stored
back to the server  on check in. Live properties must survive this.


Check out an unpublished object:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Saarland')
>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
        <div class="widget">False</div>
    ...

# XXX currently disabled because we have no unpublish
# Do a publish/unpublish cycle to set the property to false:
#
#>>> browser.getControl('Published').selected = True
#>>> browser.getControl('Save state').click()
#>>> 'There were errors' in browser.contents
#False
#>>> browser.getControl('Published').selected = False
#>>> browser.getControl('Save state').click()
#>>> 'There were errors' in browser.contents
#False

Check out:

>>> browser.getLink('Checkout').click()
>>> checked_out = browser.url

Go back to the repository and publish:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Saarland')
>>> browser.getLink('Workflow').click()
>>> browser.getControl('publish').click()
>>> 'There were errors' in browser.contents
False
>>> print browser.contents
<?xml ...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
        <div class="widget">True</div>
    ...

Go the the checked out object and check in:

>>> browser.open(checked_out)
>>> browser.getLink('Checkin').click()

The object is still published:

>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
        <div class="widget">True</div>
        ...



# XXX currently we have no unpublish
#Now try the other way round, unpublish a published document while it is checked
#out:
#
#>>> browser.getControl('Published').selected = True
#>>> browser.getControl('Save state').click()
#>>> 'There were errors' in browser.contents
#False
#>>> browser.getLink('Checkout').click()
#
#Unpublish now:
#
#>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
#...              '/2007/01/Saarland')
#>>> browser.getLink('Workflow').click()
#>>> browser.getControl('Published').selected = False
#>>> browser.getControl('Save state').click()
#>>> 'There were errors' in browser.contents
#False
#
#
#Check back in:
#
#>>> browser.open(checked_out)
#>>> browser.getLink('Checkin').click()
#
#The object is still published:
#
#>>> browser.getLink('Workflow').click()
#>>> browser.getControl('Published').selected
#False
