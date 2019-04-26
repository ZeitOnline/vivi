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

After some setup[#functional]_ we can have the principal in the variable
`principal`. We just get the clipboard for that principal via adaptation:

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

Just adding doesn't work:

>>> clipboard[u'myfeed'] = content
Traceback (most recent call last):
    ...
ValueError: Can only contain IClipboardEntry objects. Got <...> instead.

But we can adapt to ``IClipboardEntry``:

>>> clipboard[u'myfeed'] = IClipboardEntry(content)
>>> list(clipboard.keys())
[u'myfeed']


Clips
=====

Clips are folders in the clipboard. A clip is always appended at the root but
can be moved later.

>>> ignore = clipboard.addClip(u'Politik')
>>> ignore = clipboard.addClip(u'Wirtschaft')
>>> list(clipboard.keys())
[u'myfeed', u'Politik', u'Wirtschaft']

Also clips with strange titles can be added:

>>> ignore = clipboard.addClip('/bin/bash')
>>> ignore = clipboard.addClip('@property@')
>>> ignore = clipboard.addClip('++etc++site')
>>> list(clipboard.keys())
[u'myfeed', u'Politik', u'Wirtschaft', u'binbash', u'property@', u'etc++site']


Clips can be removed by just deleting them from the container:

>>> del clipboard['binbash']
>>> del clipboard['property@']
>>> del clipboard['etc++site']
>>> list(clipboard.keys())
[u'myfeed', u'Politik', u'Wirtschaft']


Adding Objects to The Clipboard via `addContent` method
=======================================================

The add content method tries to be smart where to insert content.
``addContent`` gets the following arguments: a reference_object, the content to
be added, and a desired name for the content to be added and whether content
should be put *into* the reference or after it.

1. If the ``reference\_object`` is a clip *and* it is expanded, the
   content is inserted *into* the container at first position.

2. In other cases the object is added *after* the reference object.

The model doens't know anything about being expanded or not, though. That's why
``addContent`` has the optional argument ``insert=False``.

Using the ``Politik`` clip as reference will add content *after* Politik
because Politik is collapsed right now:

>>> reference_object = clipboard['Politik']
>>> content = repository['2007']['02']['Traum-Umberto-Eco']
>>> clipboard.addContent(reference_object, content, content.__name__)
>>> list(clipboard.keys())
[u'myfeed', u'Politik', u'Traum-Umberto-Eco', u'Wirtschaft']

When using `myfeed` as reference, content will be added after it:

>>> content = repository['2007']['02']['Verfolgt']
>>> clipboard.addContent(clipboard['myfeed'], content, content.__name__)
>>> list(clipboard.keys())
[u'myfeed', u'Verfolgt', u'Politik', u'Traum-Umberto-Eco', u'Wirtschaft']


Adding the same object twice works as well:

>>> clipboard.addContent(clipboard['myfeed'], content, content.__name__)
>>> list(clipboard.keys())
[u'myfeed', u'Verfolgt-2', u'Verfolgt', u'Politik', u'Traum-Umberto-Eco',
 u'Wirtschaft']

To insert into a folder the ``insert`` argument must be True:

>>> clipboard.addContent(
...     reference_object, repository['testcontent'], u'test', insert=True)
>>> list(clipboard.keys())
[u'myfeed', u'Verfolgt-2', u'Verfolgt', u'Politik', u'Traum-Umberto-Eco',
 u'Wirtschaft']
>>> list(clipboard[u'Politik'].keys())
[u'test']

It is an error when insert is True but the reference object is not a clip:

>>> clipboard.addContent(
...     clipboard['myfeed'], repository['testcontent'], u'test', insert=True)
Traceback (most recent call last):
    ...
ValueError: `reference_object` must be a Clip to insert.



Moving Content Around
=====================

It is possible to move objects around in the clipboard. We can for instance put
documents into clips. Move the `Verfolgt` object to the `Politik` clip. Note
that move has the same semantics as add:

>>> politik = clipboard[u'Politik']
>>> verfolgt = clipboard[u'Verfolgt']
>>> clipboard.moveObject(verfolgt, politik, insert=True)
>>> list(clipboard.keys())
[u'myfeed', u'Verfolgt-2', u'Politik', u'Traum-Umberto-Eco', u'Wirtschaft']
>>> list(politik.keys())
[u'Verfolgt', u'test']


It's also possible to re-order content. Move the `Politik` clip to the front,
i.e. "after" the clipboard:

>>> clipboard.moveObject(politik, clipboard, insert=True)
>>> list(clipboard.keys())
[u'Politik',  u'myfeed', u'Verfolgt-2', u'Traum-Umberto-Eco', u'Wirtschaft']

When insert==False the object is moved after the reference object:

>>> traum = clipboard[u'Traum-Umberto-Eco']
>>> clipboard.moveObject(traum, politik)
>>> list(clipboard.keys())
[u'Politik', u'Traum-Umberto-Eco', u'myfeed', u'Verfolgt-2', u'Wirtschaft']


It's also possible to move Clips into Clips to build a deeper hierarchy:

>>> wirtschaft = clipboard[u'Wirtschaft']
>>> clipboard.moveObject(wirtschaft, politik[u'Verfolgt'])
>>> list(clipboard.keys())
[u'Politik', u'Traum-Umberto-Eco', u'myfeed', u'Verfolgt-2']
>>> list(politik.keys())
[u'Verfolgt', u'Wirtschaft', u'test']


You can drop objects onto themselves. Nothing will happen though:

>>> clipboard.moveObject(clipboard[u'Verfolgt-2'], clipboard[u'Verfolgt-2'])
>>> list(clipboard.keys())
[u'Politik', u'Traum-Umberto-Eco', u'myfeed', u'Verfolgt-2']


Erroneous Moving Attempts
=========================

One could have the idea to put a Clip into a child of itself. In this case a
ValueError is raised:

>>> clipboard.moveObject(politik, wirtschaft, insert=True)
Traceback (most recent call last):
    ...
ValueError: `obj` must not be an ancestor of `new_container`.


Footnotes
=========

.. [#functional] Setup

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()
    >>> principal = zeit.cms.testing.create_interaction()
