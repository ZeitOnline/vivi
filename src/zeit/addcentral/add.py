# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import zeit.addcentral.interfaces
import zeit.cms.repository.interfaces
import zope.component
import zope.interface


class ContentAdder(object):

    zope.interface.implements(zeit.addcentral.interfaces.IContentAdder)

    def __init__(self, request,
                 type_=None, ressort=None,
                 sub_ressort=None, year=None, month=None):
        self.request = request

        self.type_ = type_
        self.ressort = ressort
        self.sub_ressort = sub_ressort
        now = datetime.date.today()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        self.year = year
        self.month = month

    def __call__(self):
        folder = self.find_or_create_folder()
        return (zope.traversing.browser.absoluteURL(folder, self.request)
                + '/@@' + self.type_.getTaggedValue('zeit.cms.addform'))

    def find_or_create_folder(self):
        path = [self.ressort, self.sub_ressort,
                '%s-%02d' % (self.year, int(self.month))]
        repos = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

        folder = repos
        for elem in path:
            if elem is None:
                continue
            if elem not in folder:
                folder[elem] = zeit.cms.repository.folder.Folder()
            folder = folder[elem]

        return folder
