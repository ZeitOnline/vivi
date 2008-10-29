Settings
========


Global settings
---------------

The global settings are stored in an annotation on the site:

>>> import zeit.cms.settings.interfaces
>>> settings = zeit.cms.settings.interfaces.IGlobalSettings(getRootFolder())
>>> settings
<zeit.cms.settings.settings.GlobalSettings object at 0x...>

Initially the values are 26/2008:

>>> settings.default_year
2008
>>> settings.default_volume
26

Set values:

>>> settings.default_year = 2004
>>> settings.default_volume = 21


It is possible to adapt every located object to the settings:

>>> folder = getRootFolder()['repository']['online']
>>> settings = zeit.cms.settings.interfaces.IGlobalSettings(folder)
>>> settings
<zeit.cms.settings.settings.GlobalSettings object at 0x...>
>>> settings.default_year
2004
>>> settings.default_volume
21
