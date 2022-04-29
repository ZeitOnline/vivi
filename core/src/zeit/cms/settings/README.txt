Settings
========


Global settings
---------------

The global settings are stored in an annotation on the site:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
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

The current online working directory is accessible via a method. It is created
on the fly, when it does not exist:

>>> collection = settings.get_working_directory('online/$year/$volume/foo')
>>> collection.uniqueId
'http://xml.zeit.de/online/2004/21/foo/'

Make sure getting the collection does also work when it alreay exists of
course:

>>> collection = settings.get_working_directory('online/$year/$volume/foo')
>>> collection.uniqueId
'http://xml.zeit.de/online/2004/21/foo/'


Additional values can be passed:

>>> collection = settings.get_working_directory(
...     '$ressort/$year/$volume/foo', ressort='myres')
>>> collection.uniqueId
'http://xml.zeit.de/myres/2004/21/foo/'

Empty path segments are removed/ignored:

>>> collection = settings.get_working_directory(
...     '$ressort/$sub_res/$year/$volume/bar', ressort='myres', sub_res='')
>>> collection.uniqueId
'http://xml.zeit.de/myres/2004/21/bar/'


It is possible to adapt every located object to the settings:

>>> folder = getRootFolder()['repository']['online']
>>> settings = zeit.cms.settings.interfaces.IGlobalSettings(folder)
>>> settings
<zeit.cms.settings.settings.GlobalSettings object at 0x...>
>>> settings.default_year
2004
>>> settings.default_volume
21
