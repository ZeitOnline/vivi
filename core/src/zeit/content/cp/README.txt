Centerpage
==========

>>> import zeit.content.cp.centerpage
>>> cp = zeit.content.cp.centerpage.CenterPage()
>>> cp
<zeit.content.cp.centerpage.CenterPage object at 0x...>


A centerpage has three editable areas:

>>> cp['lead']
<zeit.content.cp.region.Region for lead>
>>> cp['informatives']
<zeit.content.cp.region.Region for informatives>
>>> cp['teaser-mosaic']
<zeit.content.cp.region.Region for teaser-mosaic>

Other areas are not accessible:

>>> cp['ugc-bar']
Traceback (most recent call last):
    ...
KeyError: 'ugc-bar'


Modules
+++++++

A module is part of an editable area. Modules are created using a module
factory:

>>> lead = cp['lead']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> module_factory = zope.component.getAdapter(
...     lead, zeit.content.cp.interfaces.IModuleFactory, name='teaser')
>>> module_factory.title
u'List of teasers'
>>> module = module_factory()
>>> module
<zeit.content.cp.teaser.TeaserList object at 0x...>

After calling the factory a corresponding XML node has been created:

>>> import lxml.etree
>>> print lxml.etree.tostring(lead.xml, pretty_print=True),
<region ... 
  area="lead">
  <container
    cp:class="zeit.content.cp.teaser.TeaserList"
    cp:__name__="..."/>
</region>


Modules are accessible via __getitem__ [#invalid-raises-error]_:

>>> lead[module.__name__]
<zeit.content.cp.teaser.TeaserList object at 0x...>

The lead can also be iterated:

>>> list(lead)
[<zeit.content.cp.teaser.TeaserList object at 0x...>]


.. [#invalid-raises-error]

    >>> lead['foo']
    Traceback (most recent call last):
        ...
    KeyError: 'foo'
