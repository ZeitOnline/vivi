Centerpage
==========

>>> import zeit.content.cp.centerpage
>>> cp = zeit.content.cp.centerpage.CenterPage()
>>> cp
<zeit.content.cp.centerpage.CenterPage object at 0x...>


A centerpage has three editable areas.

>>> cp['lead']
<zeit.content.cp.region.Region for lead>
>>> cp['informatives']
<zeit.content.cp.region.Region for informatives>
>>> cp['mosaic']
<zeit.content.cp.region.Region for mosaik>


Other areas are not accessible:

>>> cp['ugc-bar']
Traceback (most recent call last):
    ...
KeyError: 'ugc-bar'
