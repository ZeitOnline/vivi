=============
Zeit Workflow
=============

The workflow is state oriented. There are several states which can all be set
using the workflow tab[#browser]_[#tasks]_:

>>> browser.open('http://localhost:8080/++skin++cms/repository/testcontent')
>>> browser.getLink('Workflow').click()


States
======

The states are explained below.


Bearbeitet (Redaktion)
++++++++++++++++++++++

This state tells if the editors have finished their work. The initial value is
"no":

>>> browser.getControl('Edited').displayValue
['no']

The available options are as follows:

>>> browser.getControl('Edited').displayOptions
['no', 'yes', 'not necessary']


Korrigiert
++++++++++

Korrigiert states if the Korrektor is done. The state has the same values as
**Bearbeitet**:

>>> browser.getControl('Corrected').displayValue
['no']
>>> browser.getControl('Corrected').displayOptions
['no', 'yes', 'not necessary']


Veredelt
++++++++

Veredelt states if Links etc. were added to the document. The state has the
same values as **Bearbeitet**:

>>> browser.getControl('Refined').displayValue
['no']
>>> browser.getControl('Refined').displayOptions
['no', 'yes', 'not necessary']


Bilder hinzugefügt
++++++++++++++++++

The graphics department added images. The state has the same values as
**Bearbeitet**:

>>> browser.getControl('Images added').displayValue
['no']
>>> browser.getControl('Images added').displayOptions
['no', 'yes', 'not necessary']


Eilmeldung
++++++++++

Checking the Eilmeldung box makes the document public even though it was not
corrected etc:

>>> browser.getControl('Urgent').selected
False


Veröffentlichungszeitraum
+++++++++++++++++++++++++

An object is only visible to the public during the timespan given. Leaving the
fields empty means no restriction. This is also the default:

>>> browser.getControl('From').value
''
>>> browser.getControl('To').value
''


Transitions
===========

There are no explicit transitions defined. Instead every state attribute can
currently be set to any value at will. Let's say our document is edited:

>>> browser.getControl('Edited').displayValue = ['yes']
>>> browser.getControl('Save state only').click()
>>> browser.getControl('Edited').displayValue
['yes']

To publish the document, hit the 'publish' button:

>>> browser.getControl("publish").click()

This failed because only `edited` was set to 'yes':

>>> print browser.contents
<?xml ...
        <li class="error">publish-preconditions-not-met</li>
    ...

Use the urgent flag to override:

>>> browser.getControl('Urgent').selected = True
>>> browser.getControl("publish").click()
>>> print browser.contents
<?xml ...
        <li class="message">http://xml.zeit.de/testcontent has been scheduled for publishing.</li>
        <li class="message">Updated on 2008 4 3  12:02:00 </li>
        ...
        <div class="widget"><FORMATTED DATE>  [User]: Publication scheduled<br />
        ...


Automatic workflow properties
=============================

There are some properties which are set automatically on various occasions.


Date first released
+++++++++++++++++++

The "date first released" is the date when the object was first published.
Since publishing is done asynchronously we have to trigger processing:

>>> run_tasks()

Reload the workflow page.

>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        <label for="form.last_modified_by">
          <span>Last modified by</span>
        </label>
        <div class="hint"></div>
        <div class="widget">User</div>
        ...
      <div class="field   ">
        <label for="form.date_last_modified">
          <span>Date last modified</span>
        </label>
        <div class="hint"></div>
        <div class="widget"><span class="dateTime">2008 3 7  12:47:16 </span></div>
        ...
        ...<input class="checkboxType" checked="checked"...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
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


Publishing checked out resources
================================

There are a few race conditions regarding webdav properties. We consider the
workflow properties "live" i.e. they are only supposed to exist on the server.
When an object is checked out, all properties are copied so they can be stored
back to the server  on check in. Live properties must survive this.

Check out an unpublished object:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Saarland')
>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        ...<input class="checkboxType" id="...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
    ...

Note that the object is not published. Thus we have no "retract":

>>> browser.getControl('retract')
Traceback (most recent call last):
    ...
LookupError: label 'retract'


Do a publish/retract cycle to set the property to false:

>>> browser.getControl('Urgent').selected = True
>>> browser.getControl('publish').click()
>>> print browser.contents
<?xml ...
        <li class="message">http://xml.zeit.de/online/2007/01/Saarland has been scheduled for publishing.</li>
        ...

>>> run_tasks()
>>> browser.getLink('Workflow').click()

The retract action is protected by javascript (which doesn't matter here):

>>> print browser.contents
<?xml ...
            <input type="submit" id="form.actions.retract" name="form.actions.retract" value="Save state and retract now" class="button" />
        <script type="text/javascript">
            function confirm_Zm9ybS5hY3Rpb25zLnJldHJhY3(){
                var confirmed = confirm("Really retract? This will remove the object from all channels it is syndicated in and make it unavailable to the public!");
                if (confirmed)
                    return true;
                return false;
            }
            document.getElementById("form.actions.retract").onclick = confirm_Zm9ybS5hY3Rpb25zLnJldHJhY3;
        </script>
        ...

>>> browser.getControl('retract').click()
>>> print browser.contents
<?xml ...
        <li class="message">http://xml.zeit.de/online/2007/01/Saarland has been scheduled for retracting.</li>
        ...

Check out:

>>> browser.getLink('Checkout').click()
>>> checked_out = browser.url

Go back to the repository and publish:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Saarland')
>>> browser.getLink('Workflow').click()
>>> browser.getControl('Urgent').selected = True
>>> browser.getControl('publish').click()
>>> 'There were errors' in browser.contents
False
>>> run_tasks()
>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        ...<input class="checkboxType" checked="checked"...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
    ...

Go the the checked out object and check in:

>>> browser.open(checked_out)
>>> browser.getLink('Checkin').click()

The object is still published:

>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        ...<input class="checkboxType" checked="checked"...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
        ...

Now try the other way around, unpublish a published document while it is
checked out:

>>> browser.getControl('publish').click()
>>> print browser.contents
<?xml ...
        <li class="message">http://xml.zeit.de/online/2007/01/Saarland has been scheduled for publishing.</li>
        ...
>>> run_tasks()
>>> browser.getLink('Checkout').click()

Unpublish now:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Saarland')
>>> browser.getLink('Workflow').click()
>>> browser.getControl('retract').click()
>>> print browser.contents
<?xml ...
        <li class="message">http://xml.zeit.de/online/2007/01/Saarland has been scheduled for retracting.</li>
        ...
>>> run_tasks()
>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        ...<input class="checkboxType" id="...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
        ...

Check back in:

>>> browser.open(checked_out)
>>> browser.getLink('Checkin').click()

The object is still unpublished:

>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
        ...<input class="checkboxType" id="...
        <label for="form.published">
          <span>Published</span>
        </label>
        <div class="hint"></div>
        ...


Log
===

The workflow logs various changes in an objectlog. Verify this:

>>> print browser.contents
<?xml...
        <div class="widget"><FORMATTED DATE>  [User]: Retracted<br />...
<FORMATTED DATE>  [User]: Urgent: yes<br />
<FORMATTED DATE>  [User]: status-images-added: no<br />
<FORMATTED DATE>  [User]: status-refined: no<br />
<FORMATTED DATE>  [User]: status-corrected: no<br />
<FORMATTED DATE>  [User]: status-edited: no</div>
...

If the object log is very long, only the latest 20 entries will be
shown:

>>> zeit.workflow.browser.objectlog.ProcessForDisplay.max_entries = -20
>>> browser.getControl('Edited').displayValue = ['yes']
>>> browser.getControl('Save state only').click()

>>> for i in xrange(25):
...     browser.getControl('Edited').displayValue = ['yes']
...     browser.getControl('Save state only').click()
...     browser.getControl('Edited').displayValue = ['not necessary']
...     browser.getControl('Save state only').click()
>>> browser.contents.count('  [User]: ')
20

This is really only a matter of displaying the log; the complete object log is
still accessible[#needs-repository]_:

>>> content = repository['online']['2007']['01']['Saarland']
>>> import zeit.objectlog.interfaces
>>> log = zeit.objectlog.interfaces.ILog(content)
>>> len(list(log.get_log()))
65
>>> len(log.logs)
20


Form validation
===============

Set a very high value for publish/retract to make sure we cannot set this:

>>> browser.getControl(name='form.release_period.combination_00').value = (
...     '2040-05-06')
>>> browser.getControl(name='form.release_period.combination_01').value = (
...     '2040-05-06')
>>> browser.getControl('Save state only').click()
>>> print browser.contents
<?xml ...
 <input class="textType" id="form.release_period.combination_00" name="form.release_period.combination_00" size="20" type="text" value="2040-05-06"  />
 ...
 <span class="error">Value is too big</span>
 ...
 <input class="textType" id="form.release_period.combination_01" name="form.release_period.combination_01" size="20" type="text" value="2040-05-06"  />
 ...
 <span class="error">Value is too big</span>
 ...


Folder workflow
===============

Folders do not have a workflow. Their workflow tab has no actions but shows the
other information

>>> browser.open('http://localhost/++skin++cms/repository/online')
>>> browser.getLink('Workflow').click()
>>> print browser.contents
<?xml ...
          <span>Last modified by</span>
          ...
          <span>Date last modified</span>
          ...


.. [#browser] For UI-Tests we need a Testbrowser:

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic user:userpw')


.. [#tasks] Start processing of remote tasks

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()
    >>> import transaction

    >>> import zope.publisher.browser
    >>> import zope.security.management
    >>> import lovely.remotetask.interfaces
    >>> import lovely.remotetask.processor
    >>> tasks = zope.component.getUtility(
    ...     lovely.remotetask.interfaces.ITaskService, 'general')
    >>> def run_tasks():
    ...     principal = zeit.cms.testing.create_interaction()
    ...     transaction.abort()
    ...     tasks.process()
    ...     zope.security.management.endInteraction()

.. [#needs-repository]

    >>> import zope.component
    >>> import zeit.cms.repository.interfaces
    >>> repository = zope.component.getUtility(
    ...     zeit.cms.repository.interfaces.IRepository)
