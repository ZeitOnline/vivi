# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.browser.interfaces
import zope.component


class Sidebar(zeit.cms.browser.view.Base):

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class SiteControl(zeit.cms.browser.view.Base):

    def __call__(self):
        self.request.response.setHeader(
            'Cache-Control', 'private; max-age=360')
        return super(SiteControl, self).__call__()

    @property
    def sites(self):
        ressort = zeit.cms.content.interfaces.ICommonMetadata['ressort'].source
        ressort_terms = zope.component.getMultiAdapter(
            (ressort, self.request), zope.browser.interfaces.ITerms)
        sub_ressort = zeit.cms.content.interfaces.ICommonMetadata[
            'sub_ressort'].source

        result = []
        for ressort_name in ressort:
            result.append(dict(
                css_class='ressort',
                title=ressort_terms.getTerm(ressort_name).title,
                url=self._get_url(ressort_name)))

            bound_sub_ressort = sub_ressort(ressort_name)
            for sub_ressort_name in bound_sub_ressort:
                terms = zope.component.getMultiAdapter(
                    (bound_sub_ressort, self.request),
                    zope.browser.interfaces.ITerms)
                result.append(dict(
                    css_class='sub_ressort',
                    url=self._get_url(ressort_name, sub_ressort_name),
                    title=' ' + ressort_terms.getTerm(sub_ressort_name).title))

        return result

    def _get_url(self, ressort, sub_ressort=None):
        path = ressort.lower()
        if sub_ressort:
            path += '/' + sub_ressort.lower()
        unique_id = zeit.cms.interfaces.ID_NAMESPACE + path
        obj = zeit.cms.interfaces.ICMSContent(unique_id, None)
        if obj is not None:
            # We check for containment because this does not load the object,
            # hence is faster.
            if 'index' in obj:
                return self.url(obj, 'index')
            return self.url(obj)

        #(ressort, sub_ressort): obj

