# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import urllib
import zeit.addcentral.interfaces
import zeit.cms.repository.interfaces
import zope.browser.interfaces
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
        params = {}
        for key in ['ressort', 'sub_ressort']:
            token = self._get_token(key)
            if token is not None:
                params['form.' + key] = token
        return '%s/@@%s?%s' % (
            zope.traversing.browser.absoluteURL(folder, self.request),
            self.type_.getTaggedValue('zeit.cms.addform'),
            urllib.urlencode(params))

    def _get_token(self, field,
                   interface=zeit.addcentral.interfaces.IContentAdder):
        field = interface[field]
        source = callable(field.source) and field.source(self) or field.source
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.browser.interfaces.ITerms)
        value = field.get(self)
        if not value:
            return None
        return terms.getTerm(value).token

    def find_or_create_folder(self):
        ressort = self.ressort and self.ressort.lower()
        sub_ressort = self.sub_ressort and self.sub_ressort.lower()
        path = [ressort, sub_ressort,
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
