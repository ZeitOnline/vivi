# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.sitecontrol.interfaces
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
            'Cache-Control', 'public; max-age=360')
        return super(SiteControl, self).__call__()

    @property
    def sites(self):
        ressort = zeit.cms.content.interfaces.ICommonMetadata['ressort'].source
        ressort_terms = zope.component.getMultiAdapter(
            (ressort, self.request), zope.browser.interfaces.ITerms)
        sub_ressort = zeit.cms.content.interfaces.ICommonMetadata[
            'sub_ressort'].source

        additional = self._get_additional_sites()

        result = [dict(
            css_class='homepage',
            title=u'Homepage',
            url=self.url(self.context, 'index'))]
        for ressort_name in ressort:
            url = self._get_url(ressort_name)
            if not url:
                # If the ressort container does not exist, a sub ressort
                # container cannot exist.
                continue
            result.append(dict(
                css_class='ressort',
                title=ressort_terms.getTerm(ressort_name).title,
                url=url))

            bound_sub_ressort = sub_ressort(ressort_name)
            for sub_ressort_name in bound_sub_ressort:
                url = self._get_url(ressort_name, sub_ressort_name)
                if not url:
                    continue
                terms = zope.component.getMultiAdapter(
                    (bound_sub_ressort, self.request),
                    zope.browser.interfaces.ITerms)
                result.append(dict(
                    css_class='sub_ressort',
                    title=ressort_terms.getTerm(sub_ressort_name).title,
                    url=url))
                for site in additional.pop(
                    (ressort_name, sub_ressort_name), []):
                    site['css_class'] = 'sub_ressort ' + site['css_class']
                    result.append(site)

            for site in additional.pop(
                (ressort_name, None), []):
                site['css_class'] = 'ressort ' + site['css_class']
                result.append(site)

        for left_over in additional.values():
            result.extend(left_over)

        return result

    def _get_additional_sites(self):
        result = {}
        for name, sites in zope.component.getUtilitiesFor(
            zeit.cms.sitecontrol.interfaces.ISitesProvider):
            for content in sites:
                metadata = zeit.cms.content.interfaces.ICommonMetadata(content,
                                                                       None)
                css_class = []
                if metadata is None:
                    ressort = sub_ressort = None
                    title = content.__name__
                else:
                    ressort = metadata.ressort
                    sub_ressort = metadata.sub_ressort
                    title = metadata.title or content.__name__
                result.setdefault((ressort, sub_ressort), []).append(dict(
                    css_class=name,
                    title=title,
                    url=self.url(content)))

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
