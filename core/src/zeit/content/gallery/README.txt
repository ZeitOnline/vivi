Image Gallery
=============

Functional test setup:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())


A gallery behaves like a container, it contains images. When we create a
gallery it is empty:

>>> from zeit.content.gallery.gallery import Gallery
>>> gallery = Gallery()
>>> len(gallery)
0

Now assign an image folder. We deliberatly use one where other objects are in,
too:


>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> gallery.image_folder = repository['2006']

There is one image in the image folder, so the gallery has a length of 1 now:

>>> len(gallery)
1
>>> list(gallery.keys())
[u'DSC00109_2.JPG']



The gallery is also noted in the xml structure:

>>> import lxml.etree
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<centerpage>
  <head>
    <image-folder>http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text></text>
          <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" expires=""
            alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG"
            expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</centerpage>


Adding images to the image folder
+++++++++++++++++++++++++++++++++

Let's add an image to the image folder:

>>> import os.path
>>> import zeit.content.image.image
>>> import zeit.content.image.interfaces
>>> filename = os.path.join(os.path.dirname(__file__),
...                         'browser', 'testdata', '01.jpg')
>>> test_data = file(filename, 'rb').read()
>>> image = zeit.content.image.image.Image()
>>> image.__name__ = '01.jpg'
>>> image.data = test_data
>>> metadata = zeit.content.image.interfaces.IImageMetadata(image)
>>> metadata.copyrights = u'ZEIT online'
>>> repository['2006']['01.jpg'] = image

The gallery obviously hasn't noted this change:

>>> list(gallery.keys())
[u'DSC00109_2.JPG']

We need to call `reload_image_folder`:

>>> gallery.reload_image_folder()
>>> list(gallery.keys())
[u'DSC00109_2.JPG', u'01.jpg']

The change is reflected in the xml:

>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<centerpage>
  <head>
    <image-folder>http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text></text>
          <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <text></text>
          <image src="http://xml.zeit.de/2006/01.jpg" expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/01.jpg" expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</centerpage>

Get the entry for 01.jpg:

>>> entry = gallery['01.jpg']
>>> entry
<zeit.content.gallery.gallery.GalleryEntry object at 0x...>

The image is referenced correctly:

>>> entry.image.uniqueId
u'http://xml.zeit.de/2006/01.jpg'

We have not set any title or text for the entry, so they're empty:

>>> entry.title is None
True
>>> entry.text
u''

When we change the entry text, the change will **not** as such reflected in the
xml:

>>> entry.text = u'Seit zwei Uhr in der Früh'
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<centerpage>
  <head>
    <image-folder>http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text></text>
          <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" expires=""
            alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG"
            expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <text></text>
          <image src="http://xml.zeit.de/2006/01.jpg" expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/01.jpg"
            expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</centerpage>


When we assign the entry the change will be reflected:

>>> gallery['01.jpg'] = entry
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<centerpage>
  <head>
    <image-folder>http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text></text>
          <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <text>Seit zwei Uhr in der Fr&#195;&#188;h</text>
          <image src="http://xml.zeit.de/2006/01.jpg" expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/01.jpg" expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</centerpage>


When an `ObjectModifiedEvent` is issued for an entry, the gallery is updated as
well:

>>> import zope.event
>>> import zope.lifecycleevent
>>> entry.title = u'Der Wecker klingelt'
>>> zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(entry))
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<centerpage>
  <head>
    <image-folder>http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text></text>
          <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG"
            expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <title>Der Wecker klingelt</title>
          <text>Seit zwei Uhr in der Fr&#195;&#188;h</text>
          <image src="http://xml.zeit.de/2006/01.jpg" expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/01.jpg"
            expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</centerpage>


Let's make sure we actually can get the saved data:

>>> entry = gallery['01.jpg']
>>> entry.title
u'Der Wecker klingelt'
>>> entry.text
u'Seit zwei Uhr in der Fr\xc3\xbch'



Sorting
+++++++

The images in the gallery have a certain order. Currently it is:

>>> list(gallery.keys())
[u'DSC00109_2.JPG', u'01.jpg']

Let's change the order:

>>> gallery.updateOrder([u'01.jpg', u'DSC00109_2.JPG'])
>>> list(gallery.keys())
[u'01.jpg', u'DSC00109_2.JPG']

This is of course reflected int he XML:

>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<centerpage>
  <head>
    <image-folder>http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="01.jpg">
          <title>Der Wecker klingelt</title>
          <text>Seit zwei Uhr in der Fr&#195;&#188;h</text>
          <image src="http://xml.zeit.de/2006/01.jpg" expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/01.jpg"
            expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </thumbnail>
        </block>
        <block name="DSC00109_2.JPG">
          <text></text>
          <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG"
            expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</centerpage>

When the list passed does not match exactly the entries of the gallery, a
ValueError is raised:

>>> gallery.updateOrder([u'01.jpg'])
Traceback (most recent call last):
    ...
ValueError: The order argument must contain the same keys as the container.

Restore the orgiginal order again:

>>> gallery.updateOrder([u'DSC00109_2.JPG', u'01.jpg'])
>>> list(gallery.keys())
[u'DSC00109_2.JPG', u'01.jpg']


Container api
+++++++++++++

Explicitly check the container api methods we have not used above.

__contains__:

>>> '01.jpg' in gallery
True

Weired keys don't break the contains:

>>> '"foo]"' in gallery
False

`get`:

>>> gallery.get('01.jpg')
<zeit.content.gallery.gallery.GalleryEntry object at 0x...>
>>> gallery.get('":F34') is None
True

`items`:
>>> list(gallery.items())
[(u'DSC00109_2.JPG', <zeit.content.gallery.gallery.GalleryEntry object at 0x...>),
 (u'01.jpg', <zeit.content.gallery.gallery.GalleryEntry object at 0x...>)]

`values`:
>>> list(gallery.values())
[<zeit.content.gallery.gallery.GalleryEntry object at 0x...>,
 <zeit.content.gallery.gallery.GalleryEntry object at 0x...>]


`__iter__`:

>>> for name in gallery:
...     print "Key:", name
Key: DSC00109_2.JPG
Key: 01.jpg


Removing images from the image folder
+++++++++++++++++++++++++++++++++++++

When an image is removed from the imag folder, the gallery behaves as if it did
not know anything about the image.

Remove the 01.jpg:

>>> del repository['2006']['01.jpg']

It is now longer in the keys:

>>> list(gallery.keys())
[u'DSC00109_2.JPG']

>>> gallery['01.jpg']
Traceback (most recent call last):
    ...
KeyError: u'http://xml.zeit.de/2006/01.jpg'

Note that his has *not* changed the xml so far:

>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<centerpage>
  <head>
    <image-folder>http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text></text>
          <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG"
            expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <title>Der Wecker klingelt</title>
          <text>Seit zwei Uhr in der Fr&#195;&#188;h</text>
          <image src="http://xml.zeit.de/2006/01.jpg" expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/01.jpg"
            expires="" alt="" title="">
            <copyright>ZEIT online</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</centerpage>


When calling `reload_image_folder` the entry is removed from the xml:

>>> gallery.reload_image_folder()
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<centerpage>
  <head>
    <image-folder>http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text></text>
          <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </image>
          <thumbnail src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG"
            expires="" alt="" title="">
            <copyright xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance"
                ns0:nil="true"/>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</centerpage>


Cleanup
+++++++

>>> zope.app.component.hooks.setSite(old_site)
