=========
Clipboard
=========

A clipboard is a collection of object references.

There is actually only one clipboard per user. But users can add containers
to their clipboard to structure it. The clipboard is persistent, meaning
unlike the clipboard on windows etc. its contents is not deleted when
logging out or removed automatically.

Getting the clipbaord
=====================

After some setup[1]_ we can have the principal in the variable `principal`.
We just get the clipboard for that principal via adaptation:

>>> from zeit.cms.clipboard.interfaces import IClipboard, IClipboardEntry
>>> clipboard = IClipboard(principal)
>>> clipboard
<zeit.cms.clipboard.clipboard.Clipboard object at 0x...>
>>> clipboard.__parent__
<zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>


Adding Objects to The Clipboard via Container Interface
=======================================================

The clipboard is just a container like every other container in Zope. Initially
it is empty:

>>> list(clipboard.keys())
[]

Let's get a content object from the repository and add it:

>>> import zope.component
>>> from zeit.cms.repository.interfaces import IRepository
>>> repository = zope.component.getUtility(IRepository)
>>> content = repository['politik.feed']
>>> clipboard[u'myfeed'] = content
Traceback (most recent call last):
    ...
ValueError: Can only contain IClipboardEntry objects. Got <...> instead.
>>> clipboard[u'myfeed'] = IClipboardEntry(content)
>>> list(clipboard.keys())
[u'myfeed']


Adding Objects to The Clipboard via `addContent` method
=======================================================

The add content method tries to be smart where to insert content. There are two
cases.

`refrence_object` is an ICMSContent
+++++++++++++++++++++++++++++++++++

When the `refrence_object` provides ICMSContent, the object is added *after*
the `reference_object`. So using 'myfeed' as reference inserts after it:

>>> reference_object = clipboard['myfeed']
>>> reference_object
<zeit.cms.clipboard.entry.Entry object at 0x...>
>>> content = repository['2007']['02']['Traum-Umberto-Eco']
>>> clipboard.addContent(reference_object, content, content.__name__)
>>> list(clipboard.keys())
[u'myfeed', u'Traum-Umberto-Eco']

When still using `myfeed` we insert between `Traum...` and the feed:

>>> content = repository['2007']['02']['Verfolgt']
>>> clipboard.addContent(reference_object, content, content.__name__)
>>> list(clipboard.keys())
[u'myfeed', u'Verfolgt', u'Traum-Umberto-Eco']


Adding the same object twice works as well:

>>> clipboard.addContent(reference_object, content, content.__name__)
>>> list(clipboard.keys())
[u'myfeed', u'Verfolgt-2', u'Verfolgt', u'Traum-Umberto-Eco']


`reference_object` is a Container
+++++++++++++++++++++++++++++++++

When the `reference_object` is a container, but *not* an ICMSContent, the
object is added at first position. This is also true for the clipboard itself:


>>> content = repository['2007']['02']['Vita']
>>> clipboard.addContent(clipboard, content, content.__name__)
>>> list(clipboard.keys())
[u'Vita', u'myfeed', u'Verfolgt-2', u'Verfolgt', u'Traum-Umberto-Eco']


Adding Clips
============

Clips are folders in the clipboard. A clip is alwasy appended at the root:

>>> clipboard.addClip(u'Politik')
>>> clipboard.addClip(u'Wirtschaft')
>>> list(clipboard.keys())
[u'Vita', u'myfeed', u'Verfolgt-2', u'Verfolgt', u'Traum-Umberto-Eco',
 u'Politik', u'Wirtschaft']


Moving Content Around
=====================

It is possible to move objects around in the clipboard. We can for instance put
documents into clips. Move the `Verfolgt` object to the `Politik` clip.:

>>> politik = clipboard[u'Politik']
>>> verfolgt = clipboard[u'Verfolgt']
>>> clipboard.moveObject(verfolgt, politik)
>>> list(clipboard.keys())
[u'Vita', u'myfeed', u'Verfolgt-2', u'Traum-Umberto-Eco',
 u'Politik', u'Wirtschaft']
>>> list(politik.keys())
[u'Verfolgt']


It's also possible to re-order content. Move the `Politik` clip to the front,
i.e. "after" the clipboard:

>>> vita = clipboard[u'Vita']
>>> clipboard.moveObject(politik, clipboard)
>>> list(clipboard.keys())
[u'Politik', u'Vita', u'myfeed', u'Verfolgt-2', u'Traum-Umberto-Eco',
 u'Wirtschaft']

When using a non-folderish object as "drop target" the object will be moved
*after* the drop target. Move `traum` after `vita`:

>>> traum = clipboard[u'Traum-Umberto-Eco']
>>> clipboard.moveObject(traum, vita)
>>> list(clipboard.keys())
[u'Politik', u'Vita', u'Traum-Umberto-Eco', u'myfeed', u'Verfolgt-2',
 u'Wirtschaft']



It's also possible to move Clips into Clips to build a deeper hierarchy:

>>> wirtschaft = clipboard[u'Wirtschaft']
>>> clipboard.moveObject(wirtschaft, politik)
>>> list(clipboard.keys())
[u'Politik', u'Vita', u'Traum-Umberto-Eco', u'myfeed', u'Verfolgt-2']
>>> list(politik.keys())
[u'Wirtschaft', u'Verfolgt']


You can drop objects onto themselves. Nothing will happen though:

>>> clipboard.moveObject(verfolgt, verfolgt)
>>> list(clipboard.keys())
[u'Politik', u'Vita', u'Traum-Umberto-Eco', u'myfeed', u'Verfolgt-2']


Erroneous Moving Attempts
=========================

One could have the idea to put a Clip into a child of itself. In this case a
ValueError is raised:

>>> clipboard.moveObject(politik, wirtschaft)
Traceback (most recent call last):
    ...
ValueError: `obj` must not be an ancestor of `new_container`.

Cleanup
=======

After the tests we clean up:

>>> zope.security.management.endInteraction()
>>> zope.app.component.hooks.setSite(old_site)
    


Footnotes
=========

.. [1] Setup

    We need to set the site since we're a functional test:

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    We also need an interaction as we needs to get the principal:

    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'zope.mgr')
    >>> participation = zope.security.testing.Participation(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(participation)
