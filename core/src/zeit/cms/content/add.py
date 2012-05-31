# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import grokcore.component as grok
import urllib
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zope.browser.interfaces
import zope.component
import zope.interface


class ContentAdder(object):

    zope.interface.implements(zeit.cms.content.interfaces.IContentAdder)

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
        # we want to register the IAddLocation adapter for the content-type,
        # which is an *interface*. We need a representative object providing
        # that interface to be able to ask for those adapters, since
        # zope.component looks for provides when an interface is required, and
        # interfaces don't provide themselves.
        dummy = type(self.type_.__name__, (object,), {})()
        zope.interface.alsoProvides(dummy, self.type_)
        context = zope.component.getMultiAdapter(
            (dummy, self), zeit.cms.content.interfaces.IAddLocation)

        params = {}
        for key in ['ressort', 'sub_ressort']:
            token = self._get_token(key)
            if token is not None:
                params['form.' + key] = token
        return '%s/@@%s?%s' % (
            zope.traversing.browser.absoluteURL(context, self.request),
            self.type_.getTaggedValue('zeit.cms.addform'),
            urllib.urlencode(params))

    def _get_token(self, field,
                   interface=zeit.cms.content.interfaces.IContentAdder):
        field = interface[field]
        source = callable(field.source) and field.source(self) or field.source
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.browser.interfaces.ITerms)
        value = field.get(self)
        if not value:
            return None
        return terms.getTerm(value).token


@grok.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.content.interfaces.IContentAdder)
@grok.implementer(zeit.cms.content.interfaces.IAddLocation)
def ressort_year_folder(type_, adder):
    ressort = adder.ressort and adder.ressort.lower()
    sub_ressort = adder.sub_ressort and adder.sub_ressort.lower()
    return find_or_create_folder(
        ressort, sub_ressort, '%s-%02d' % (adder.year, int(adder.month)))


def find_or_create_folder(*path_elements):
    repos = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)

    folder = repos
    for elem in path_elements:
        if elem is None:
            continue
        if elem not in folder:
            folder[elem] = zeit.cms.repository.folder.Folder()
        folder = folder[elem]

    return folder
