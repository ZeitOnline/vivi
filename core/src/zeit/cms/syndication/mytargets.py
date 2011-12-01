# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent
import BTrees

import zope.annotation
import zope.component
import zope.interface

import zope.app.container.contained
import zope.app.keyreference.interfaces

import zeit.cms.content.property
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces

import zeit.cms.syndication.interfaces


class MySyndicationTargets(persistent.Persistent,
                           zope.app.container.contained.Contained):

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IMySyndicationTargets)
    zope.component.adapts(zeit.cms.workingcopy.interfaces.IWorkingcopy)

    default_targets = (
        'http://xml.zeit.de/hp_channels/r07_hp_aufmacher',
        'http://xml.zeit.de/hp_channels/r07_hp_knopf',
        'http://xml.zeit.de/hp_channels/channel_news',
        'http://xml.zeit.de/hp_channels/channel_magazin',
        'http://xml.zeit.de/hp_channels/channel_exklusiv_reform.xm',
        'http://xml.zeit.de/deutschland/channel_deutschland',
        'http://xml.zeit.de/international/channel_international',
        'http://xml.zeit.de/meinung/channel_meinung',
        'http://xml.zeit.de/wirtschaft/channel_wirtschaft',
        'http://xml.zeit.de/wissen/channel_wissen',
        'http://xml.zeit.de/kultur/channel_kultur',
        'http://xml.zeit.de/leben/channel_leben',
        'http://xml.zeit.de/bildung/channel_bildung',
        'http://xml.zeit.de/musik/channel_musik',
    )

    def __init__(self):
        self.targets = BTrees.family32.OI.TreeSet()
        self._initalize_defaults()

    def add(self, feed):
        self.targets.insert(
            zope.app.keyreference.interfaces.IKeyReference(feed))

    def remove(self, feed):
        try:
            self.targets.remove(
                zope.app.keyreference.interfaces.IKeyReference(feed))
        except KeyError:
            pass

    def __contains__(self, feed):
        return (zope.app.keyreference.interfaces.IKeyReference(feed)
                in self.targets)

    def __iter__(self):
        for keyref in self.targets:
            try:
                yield keyref()
            except KeyError:
                pass

    def _initalize_defaults(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        for id in self.default_targets:
            try:
                feed = repository.getContent(id)
            except KeyError:
                continue
            self.add(feed)


targetFactory = zope.annotation.factory(MySyndicationTargets)
