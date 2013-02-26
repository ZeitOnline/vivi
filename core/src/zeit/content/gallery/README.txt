Image Gallery
=============

A gallery behaves like a container, it contains images. When we create a
gallery it is empty[#functional]_:

>>> from zeit.content.gallery.gallery import Gallery
>>> gallery = Gallery()
>>> len(gallery)
0

The gallery provides the IGallery and IEditorialContent interfaces:

>>> import zope.interface.verify
>>> import zeit.cms.interfaces
>>> import zeit.content.gallery.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.content.gallery.interfaces.IGallery, gallery)
True
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IEditorialContent, gallery)
True

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
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>


Adding images to the image folder
+++++++++++++++++++++++++++++++++

Let's add an image to the image folder:

>>> import zeit.content.gallery.testing
>>> zeit.content.gallery.testing.add_image('2006', '01.jpg')

The gallery obviously hasn't noted this change:

>>> list(gallery.keys())
[u'DSC00109_2.JPG']

We need to call `reload_image_folder`:

>>> gallery.reload_image_folder()
>>> list(gallery.keys())
[u'DSC00109_2.JPG', u'01.jpg']

The change is reflected in the xml:

>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <caption>Nice image</caption>
          <image ...src="http://xml.zeit.de/2006/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>

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
None

The caption is pre-filled with the caption of the image:

>>> entry.caption
u'Nice image'

When we change the entry text, the change will **not** as such reflected in the
xml:

>>> entry.text = lxml.objectify.E.text(
...     lxml.objectify.E.p(u'Seit zwei Uhr in der Früh'))
>>> entry.caption = u'Gallery &amp; <br/>caption'
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <caption>Nice image</caption>
          <image ...src="http://xml.zeit.de/2006/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>


When we assign the entry the change will be reflected:

>>> gallery['01.jpg'] = entry
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <text xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <p py:pytype="str">Seit zwei Uhr in der Fr&#195;&#188;h</p>
          </text>
          <caption>Gallery &amp; <br/>caption</caption>
          <image ...src="http://xml.zeit.de/2006/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>


When an `ObjectModifiedEvent` is issued for an entry, the gallery is updated as
well:

>>> import zope.event
>>> import zope.lifecycleevent
>>> entry.title = u'Der Wecker klingelt'
>>> zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(entry))
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <title py:pytype="str">Der Wecker klingelt</title>
          <text xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <p py:pytype="str">Seit zwei Uhr in der Fr&#195;&#188;h</p>
          </text>
          <caption>Gallery &amp; <br/>caption</caption>
          <image ...src="http://xml.zeit.de/2006/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>


Let's make sure we actually can get the saved data:

>>> entry = gallery['01.jpg']
>>> entry.title
u'Der Wecker klingelt'
>>> entry.text
<Element text at ...>
>>> entry.text['p']
u'Seit zwei Uhr in der Fr\xc3\xbch'
>>> entry.caption
u'Gallery &amp; <br/>caption'


Entry layout
++++++++++++

Each entry can have a different layout. This is defined by a source:

>>> field = zeit.content.gallery.interfaces.IGalleryEntry['layout']
>>> list(field.vocabulary)
[u'hidden', u'image-only']

Let's set a layout on 01.jpg:

>>> entry = gallery['01.jpg']
>>> entry.layout is None
True
>>> entry.layout = u'image-only'
>>> gallery['01.jpg'] = entry
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
        <block layout="image-only" name="01.jpg">
          <title py:pytype="str">Der Wecker klingelt</title>
          <text xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <p py:pytype="str">Seit zwei Uhr in der Fr&#195;&#188;h</p>
          </text>
          <caption>Gallery &amp; <br/>caption</caption>
          <image ...src="http://xml.zeit.de/2006/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>


When we set the layout to None again, the layout attribute is removed:

>>> entry = gallery['01.jpg']
>>> entry.layout
u'image-only'
>>> entry.layout = None
>>> gallery['01.jpg'] = entry
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <title py:pytype="str">Der Wecker klingelt</title>
          <text xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <p py:pytype="str">Seit zwei Uhr in der Fr&#195;&#188;h</p>
          </text>
          <caption>Gallery &amp; <br/>caption</caption>
          <image ...src="http://xml.zeit.de/2006/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>


Crops
+++++

When using zeit.imp to crop images, it will store the cropped images under the
same name prefix. zeit.imp needs to retrieve those again, so GalleryEntry has
a helper method to return images that are crops of its image:

>>> entry = gallery['01.jpg']
>>> entry.crops
[]
>>> zeit.content.gallery.testing.add_image('2006', '02.jpg', '01.jpg-10x10.jpg')
>>> gallery.reload_image_folder()
>>> entry = gallery['01.jpg-10x10.jpg']
>>> entry.is_crop_of = '01.jpg'
>>> gallery['01.jpg-10x10.jpg'] = entry
>>> entry = gallery['01.jpg']
>>> entry.crops[0].__name__
u'01.jpg-10x10.jpg'
>>> del repository['2006']['01.jpg-10x10.jpg']
>>> gallery.reload_image_folder()

Additionally, each entry stores whether it was generated by cropping and what
it was cropped from:

>>> entry = gallery['01.jpg']
>>> entry.is_crop_of is None
True
>>> entry.is_crop_of = 'foo'
>>> gallery['01.jpg'] = entry
>>> entry = gallery['01.jpg']
>>> entry.is_crop_of
'foo'

reset for following tests:

>>> entry.is_crop_of = None
>>> gallery['01.jpg'] = entry
>>> gallery['01.jpg'].is_crop_of is None
True


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
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="01.jpg">
          <title py:pytype="str">Der Wecker klingelt</title>
          <text xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <p py:pytype="str">Seit zwei Uhr in der Fr&#195;&#188;h</p>
          </text>
          <caption>Gallery &amp; <br/>caption</caption>
          <image ...src="http://xml.zeit.de/2006/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>

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
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
        <block name="01.jpg">
          <title py:pytype="str">Der Wecker klingelt</title>
          <text xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <p py:pytype="str">Seit zwei Uhr in der Fr&#195;&#188;h</p>
          </text>
          <caption>Gallery &amp; <br/>caption</caption>
          <image ...src="http://xml.zeit.de/2006/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/01.jpg" type="jpg"...>
            <bu ...>Nice image</bu>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>


When calling `reload_image_folder` the entry is removed from the xml:

>>> gallery.reload_image_folder()
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <image-folder py:pytype="str">http://xml.zeit.de/2006</image-folder>
  </head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </image>
          <thumbnail ...src="http://xml.zeit.de/2006/thumbnails/DSC00109_2.JPG" type="JPG"...>
            <bu xsi:nil="true"/>
            <copyright ...>...</copyright>
          </thumbnail>
        </block>
      </container>
    </column>
  </body>
</gallery>

Reloading the image folder will also re-create all the thumbnails. The
thumbnail of the removed image is also removed:

>>> repository['2006']['thumbnails'].keys()
[u'DSC00109_2.JPG']


At one point we had galleries with an empty caption-tag which broke
the system. Make sure this doesn't happen any more:

>>> gallery.xml['body']['column'][1]['container']['block'].append(
...     lxml.objectify.E.caption())
>>> list(gallery.values())
[<zeit.content.gallery.gallery.GalleryEntry object at 0x...>]


Old XML format
==============

The old xml format is a bit more lazy. Let's add the second image again:

>>> zeit.content.gallery.testing.add_image('2006', '01.jpg')
>>> gallery.xml = lxml.objectify.XML(u"""\
...     <gallery>
...       <head>
...       </head>
...       <body>
...         <column layout="left"/>
...         <column layout="right">
...           <container>
...             <block>
...               <text>
...                  Im holländischen Kapitänsduell mit Wolfsburgs Kevin Hofland zeigte sich Rafael van der Vaart (links) engagiert wie eh und je. Der entscheidende Mann beim Heimspiel des Hamburger SV gegen den VfL Wolfsburg hieß aber...&#13;
...                  <a href="fooo">link</a>
...               </text>
...               <image expires="2007-04-09" src="/cms/work/2006/DSC00109_2.JPG" 
...                     width="380" align="left">
...                 <copyright>© Martin Rose/Getty Images</copyright>
...                 BILD 
...               </image>
...             </block>
...             <block>
...               <image expires="2007-04-09" src="/cms/work/2006/01.jpg" width="380"
...                 align="left">
...                 <copyright>© Martin Rose/Getty Images</copyright> BILD </image>
...             </block>
...           </container>
...         </column>
...       </body>
...     </gallery>""")


There are some major differences to the new xml:

1. The image folder is not explicitly noted and needs to be decuced.
2. The blocks containing the images do not have names.
3. The <text> node is optional.
4. Text can be directly in the <text> node.

The image folder is /2006, decuced from /cms/work/2006/DSC00109_2.jpg:

>>> gallery.image_folder.uniqueId
u'http://xml.zeit.de/2006'

The keys also correct(ed) and the names are set:

>>> list(gallery.keys())
[u'DSC00109_2.JPG', u'01.jpg'] 
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery>
  <head>
      <image-folder xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str">http://xml.zeit.de/2006</image-folder></head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
            <text...>
               <p>
                 Im holl&#195;&#164;ndischen Kapit&#195;&#164;nsduell mit Wolfsburgs Kevin Hofland zeigte sich Rafael van der Vaart (links) engagiert wie eh und je. Der entscheidende Mann beim Heimspiel des Hamburger SV gegen den VfL Wolfsburg hie&#195;&#159; aber...&#13;
                 <a href="fooo">link</a>
               </p>
             </text>
          <image ... src="http://xml.zeit.de/2006/DSC00109_2.JPG"...
          <thumbnail...
        </block>
        <block name="01.jpg">
          <text.../>
          <caption>Nice image</caption>
          <image ... src="http://xml.zeit.de/2006/01.jpg"...
             <bu ...>Nice image</bu>
             <copyright py:pytype="str" link="http://www.zeit.de">ZEIT online</copyright>
           </image>
           <thumbnail...
        </block>
      </container>
    </column>
  </body>
</gallery>


Getting an gallery entry w/o text element used to break (bug #4042) but works
now:

>>> gallery['01.jpg']
<zeit.content.gallery.gallery.GalleryEntry object at 0x...>

The entries' text is wrapped in a <p> node:

>>> entry = gallery['DSC00109_2.JPG']
>>> entry.text
<Element text at ...>
>>> print lxml.etree.tostring(entry.text, pretty_print=True)
<text xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <p>
                 Im holl&#195;&#164;ndischen Kapit&#195;&#164;nsduell mit Wolfsburgs Kevin Hofland zeigte sich Rafael van der Vaart (links) engagiert wie eh und je. Der entscheidende Mann beim Heimspiel des Hamburger SV gegen den VfL Wolfsburg hie&#195;&#159; aber...&#13;
                 <a href="fooo">link</a>
              </p>
</text>



Let's make sure this also works, when the image urls are not starting wich
/cms/work but are already convertet to http://xml.zeit.de urls:

>>> gallery.xml = lxml.objectify.XML(u"""\
...     <gallery>
...       <head>
...       </head>
...       <body>
...         <column layout="left"/>
...         <column layout="right">
...           <container>
...             <block>
...               <text>
...                  Im holländischen Kapitänsduell mit Wolfsburgs Kevin Hofland zeigte sich Rafael van der Vaart (links) engagiert wie eh und je. Der entscheidende Mann beim Heimspiel des Hamburger SV gegen den VfL Wolfsburg hieß aber...&#13;
...               </text>
...               <image expires="2007-04-09" src="http://xml.zeit.de/2006/DSC00109_2.JPG" 
...                     width="380" align="left">
...                 <copyright>© Martin Rose/Getty Images</copyright>
...                 BILD 
...               </image>
...             </block>
...             <block>
...               <image expires="2007-04-09" src="http://xml.zeit.de/2006/01.jpg" width="380"
...                 align="left">
...                 <copyright>© Martin Rose/Getty Images</copyright> BILD </image>
...             </block>
...           </container>
...         </column>
...       </body>
...     </gallery>""")


The image folder is resolved correcty, too:

>>> gallery.image_folder.uniqueId
u'http://xml.zeit.de/2006'

The keys also correct(ed) and the names are set:

>>> list(gallery.keys())
[u'DSC00109_2.JPG', u'01.jpg'] 
>>> print lxml.etree.tostring(gallery.xml, pretty_print=True)
<gallery>
  <head>
      <image-folder xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str">http://xml.zeit.de/2006</image-folder></head>
  <body>
    <column layout="left"/>
    <column layout="right">
      <container>
        <block name="DSC00109_2.JPG">
          <text...>
            <p ...>
                 Im holl&#195;&#164;ndischen Kapit&#195;&#164;nsduell mit Wolfsburgs Kevin Hofland zeigte sich Rafael van der Vaart (links) engagiert wie eh und je. Der entscheidende Mann beim Heimspiel des Hamburger SV gegen den VfL Wolfsburg hie&#195;&#159; aber...&#13;
             </p>
          </text>
          <image ... src="http://xml.zeit.de/2006/DSC00109_2.JPG"...
          <thumbnail...
        </block>
        <block name="01.jpg">
          <text.../>
          <caption...
          <image ... src="http://xml.zeit.de/2006/01.jpg" ...
          <thumbnail...
        </block>
      </container>
    </column>
  </body>
</gallery>

.. [#functional]

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()


Searchable text
===============

>>> adapter = zope.index.text.interfaces.ISearchableText(gallery)
>>> adapter.getSearchableText()
[u'Im holl\xc3\xa4ndischen Kapit\xc3\xa4nsduell mit Wolfsburgs Kevin Hofland zeigte sich Rafael van der Vaart (links) engagiert wie eh und je. Der entscheidende Mann beim Heimspiel des Hamburger SV gegen den VfL Wolfsburg hie\xc3\x9f aber...']
