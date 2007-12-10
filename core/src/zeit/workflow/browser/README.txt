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
"nein":

>>> browser.getControl('Bearbeitet').displayValue
['nein']

The available options are as follows:

>>> browser.getControl('Bearbeitet').displayOptions
['nein', 'ja', 'nicht n\xc3\xb6tig']


Korrigiert 
++++++++++

Korrigiert states if the Korrektor is done. The state has the same values as
**Bearbeitet**:

>>> browser.getControl('Korrigiert').displayValue
['nein']
>>> browser.getControl('Korrigiert').displayOptions
['nein', 'ja', 'nicht n\xc3\xb6tig']

Veredelt
++++++++

Veredelt states if Links etc. were added to the document. The state has the
same values as **Bearbeitet**:

>>> browser.getControl('Veredelt').displayValue
['nein']
>>> browser.getControl('Veredelt').displayOptions
['nein', 'ja', 'nicht n\xc3\xb6tig']


Bilder hinzugefügt
++++++++++++++++++

The graphics department adds image. The state has the same values as
**Bearbeitet**:

>>> browser.getControl('Bilder hinzugefügt').displayValue
['nein']
>>> browser.getControl('Bilder hinzugefügt').displayOptions
['nein', 'ja', 'nicht n\xc3\xb6tig']


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

>>> browser.getControl('Bearbeitet').displayValue = ['ja']
>>> browser.getControl('Apply').click()
>>> browser.getControl('Bearbeitet').displayValue
['ja']

# Add some more tests...



.. [1] For UI-Tests we need a Testbrowser:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

