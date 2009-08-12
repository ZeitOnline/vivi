# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime, timedelta
from zeit.find.daterange import DATE_RANGES
import zc.iso8601.parse
import zc.resourcelibrary
import zeit.cms.browser.interfaces
import zeit.cms.browser.preview
import zeit.cms.browser.view
import zeit.cms.clipboard.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.find.search
import zope.component
import zope.i18n
import zope.interface
import zope.viewlet.interfaces


class JSONView(zeit.cms.browser.view.JSON):

    resource_library = 'zeit.find'

    def url(self, view, uniqueId):
        return super(JSONView, self).url(
            self.context, '%s?uniqueId=%s' % (view, uniqueId))


class SearchForm(JSONView):

    template = 'search_form.jsont'

    def json(self):
        return dict(
            ressorts=self.ressorts,
            types=self.types)

    @property
    def ressorts(self):
        return [
            dict(ressort=ressort)
            for ressort in zeit.cms.content.sources.NavigationSource()]

    @property
    def types(self):
        result = []
        for name, interface in zope.component.getUtilitiesFor(
            zeit.cms.interfaces.ICMSContentType):
            type_ = interface.queryTaggedValue('zeit.cms.type') or name
            title = zope.i18n.translate(
                interface.queryTaggedValue('zeit.cms.title') or type_,
                context=self.request)
            result.append(dict(
                title=title,
                type=type_,
            ))
        return sorted(result, key=lambda r:r['title'])


def get_favorited_css_class(favorited):
    return 'toggle_favorited ' + (
        'favorited' if favorited else 'not_favorited')


class SearchResult(JSONView):

    template = 'search_result.jsont'

    def sort_order(self):
        return self.request.get('sort_order', 'relevance')

    def json(self):
        try:
            q = form_query(self.request)
        except InputError, e:
            error = unicode(e)
            return {'template': 'no_search_result.jsont', "error": error}
        if q is None:
            return {'template': 'no_search_result.jsont'}

        # record any known favorites
        # XXX this isn't that pleasant to do every search,
        # but we need to match the uniqueIds quickly during
        # the search results
        favorite_uniqueIds = set()
        for favorite in get_favorites(self.request).values():
            uniqueId = favorite.referenced_unique_id
            if not uniqueId:
                continue
            favorite_uniqueIds.add(uniqueId)

        r = self.resources
        results = []
        application_url = self.request.getApplicationURL()
        for result in zeit.find.search.search(q, self.sort_order()):
            uniqueId = result.get('uniqueId', '')
            title = result.get('teaser_title')
            if not title:
                title = result.get('title')
            if not title:
                title = uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE,
                                         '', 1)
            favorited = uniqueId in favorite_uniqueIds
            last_semantic_change = result.get('last-semantic-change')
            if last_semantic_change is not None:
                dt = zc.iso8601.parse.datetimetz(result['last-semantic-change'])
            else:
                dt = None

            volume = result.get('volume')
            year = result.get('year')
            if volume and year:
                volume_year = '%s/%s' % (volume, year)
            else:
                volume_year = ''

            published = result.get('published', 'published')
            if published == 'published':
                publication_status = r['published.png']()
            elif published == 'not-published':
                publication_status = r['unpublished.png']()
            elif published == 'published-with-changes':
                publication_status = r['published_new.png']()
            else:
                # XXX fallback status is always published
                publication_status = r['published.png']()

            if dt:
                start_date = dt.date()
                end_date = start_date + timedelta(1)
            else:
                start_date = None
                end_date = None

            icon = result.get('icon')
            if icon:
                icon = application_url + icon
            preview_url = zeit.cms.browser.preview.get_preview_url(
                'preview-prefix', uniqueId)
            results.append({
                    'application_url': application_url,
                    'arrow': r['arrow_right.png'](),
                    'authors': result.get('authors', []),
                    'date': format_date(dt),
                    'end_date': format_date(end_date),
                    'favorite_url': self.url('toggle_favorited', uniqueId),
                    'favorited': favorited,
                    'favorited_css_class': get_favorited_css_class(favorited),
                    'icon': icon,
                    'preview_url': preview_url,
                    'publication_status': publication_status,
                    'related_url': self.url('expanded_search_result', uniqueId),
                    'start_date': format_date(start_date),
                    'supertitle': result.get('supertitle', ''),
                    'teaser_title': title,
                    'topic': result.get('ressort', ''),
                    'uniqueId': uniqueId,
                    'volume_year': volume_year,
                    })
        if not results:
            return {'template': 'no_search_result.jsont'}
        return {'results': results}


class ResultFilters(JSONView):

    template = 'result_filters.jsont'

    def json(self):
        try:
            q = form_query(self.request)
        except InputError:
            # the real input errors are handled by the main form; by itself
            # this should never receive broken input
            q = None

        if q is None:
            return {'template': 'no_result_filters.jsont'}

        (time_counts, topic_counts,
         author_counts, type_counts) = zeit.find.search.counts(q)

        result = {
            'topic_entries': self.entries(topic_counts),
            'time_entries': self.time_entries(time_counts),
            'type_entries': self.type_entries(type_counts),
            'author_entries': self.entries(author_counts),
            }
        if not (result['topic_entries'] or result['time_entries'] or
                result['type_entries'] or result['author_entries']):
            return {'template': 'no_result_filters.jsont'}
        return result

    def time_entries(self, counts):
        result = []
        for ((name, count),
             (name2, (start_date, end_date)))  in zip(counts, DATE_RANGES):
            if count == 0:
                continue
            result.append(dict(title=name,
                               amount=format_amount(count),
                               start_date=format_date(start_date),
                               end_date=format_date(end_date)))
        return result

    def type_entries(self, counts):
        types = {}
        for name, interface in zope.component.getUtilitiesFor(
            zeit.cms.interfaces.ICMSContentType):
            type_ = interface.queryTaggedValue('zeit.cms.type')
            if type_:
                types[type_] = interface

        result = []
        for type_name, count in counts:
            interface = types.get(type_name)
            title = None
            if interface:
                title = interface.queryTaggedValue('zeit.cms.title')
            if not title:
                title = type_name
            result.append(dict(
                amount=format_amount(count),
                title=zope.i18n.translate(title, context=self.request),
                type=type_name,
            ))
        return result

    def entries(self, counts):
        result = []
        for name, count in counts:
            result.append(dict(title=name,
                               amount=format_amount(count)))
        return result


class ExpandedSearchResult(JSONView):

    template = 'expanded_search_result.jsont'

    def json(self):
        uniqueId = self.request.get('uniqueId')
        if not uniqueId:
            return {'template': 'no_expanded_search_result.jsont'}

        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        related_content = zeit.cms.related.interfaces.IRelatedContent(content,
                                                                      None)
        if related_content is None:
            return {'template': 'no_expanded_search_result.jsont'}

        related = related_content.related

        r = self.resources
        results = []
        for content in related:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                content, None)
            if metadata is None:
                continue

            date = zeit.cms.content.interfaces.ISemanticChange(
                content).last_semantic_change
            publication_status = self.render_publication_status(content)
            results.append({
                    'uniqueId': content.uniqueId,
                    'publication_status': publication_status,
                    'short_teaser_title': metadata.shortTeaserTitle or '',
                    'short_teaser_text': metadata.shortTeaserText or '',
                    'date': format_date(date),
                    })
        if not results:
            return {'template': 'no_expanded_search_result.jsont'}

        return {'results': results}

    def render_publication_status(self, content):
        viewlet_manager = zope.component.getMultiAdapter(
            (content, self.request, self),
            zope.viewlet.interfaces.IViewletManager,
            name='zeit.cms.workflow-indicator')
        viewlet_manager.update()
        return viewlet_manager.render()


class ToggleFavorited(JSONView):

    template = 'toggle_favorited.jsont'

    def json(self):
        content = zeit.cms.interfaces.ICMSContent(
            self.request.get('uniqueId'))
        favorites = get_favorites(self.request)
        if content.__name__ in favorites:
            del favorites[content.__name__]
            favorited = False
        else:
            favorites[content.__name__] = (
                zeit.cms.clipboard.interfaces.IClipboardEntry(content))
            favorited = True
        return {
            'favorited_css_class': get_favorited_css_class(favorited),
        }


class Favorites(JSONView):
    template = 'search_result.jsont'

    def result_entry(self, content):
        r = self.resources
        uniqueId = content.uniqueId

        metadata = zeit.cms.content.interfaces.ICommonMetadata(content, None)

        if metadata:
            if metadata.authors:
                authors = list(metadata.authors)
            else:
                authors = []
            teaser_title = metadata.teaserTitle or ''
            supertitle = metadata.supertitle or ''
            year = metadata.year or ''
            volume = metadata.volume or ''
            if year and volume:
                volume_year = '%s/%s' % (volume, year)
            else:
                volume_year = ''
            topic = metadata.ressort or ''
        else:
            authors = []
            teaser_title = ''
            supertitle = ''
            teaser_text = ''
            volume_year = ''
            topic = ''

        date = zeit.cms.content.interfaces.ISemanticChange(
            content).last_semantic_change

        if date:
            start_date = date.date()
            end_date = start_date + timedelta(1)
        else:
            start_date = None
            end_date = None

        preview_url = zeit.cms.browser.preview.get_preview_url(
            'preview-prefix', uniqueId)

        icon = zope.component.queryMultiAdapter(
            (content, self.request), name='zmi_icon')
        if icon is None:
            icon = ''
        else:
            icon = icon.url()

        return {
            'application_url': self.request.getApplicationURL(),
            'arrow': r['arrow_right.png'](),
            'authors': authors,
            'date': format_date(date),
            'end_date': format_date(end_date),
            'favorite_url': self.url('toggle_favorited', uniqueId),
            'favorited': True,
            'favorited_css_class': get_favorited_css_class(True),
            'icon': icon,
            'preview_url': preview_url,
            'publication_status': r['published.png'](),
            'related_url': self.url('expanded_search_result', uniqueId),
            'start_date': format_date(start_date),
            'supertitle': supertitle,
            'teaser_title': teaser_title,
            'topic': topic,
            'uniqueId': uniqueId,
            'volume_year': volume_year,
            }

    def json(self):
        favorites = get_favorites(self.request)
        result = []
        for fav in favorites.values():
            obj = fav.references
            if obj is None:
                continue
            result.append(self.result_entry(obj))
        return {"results": result}


class ForThisPage(JSONView):

    template = 'for-this-page.jsont'

    def json(self):
        metadata = zeit.cms.content.interfaces.ICommonMetadata(self.context,
                                                               None)
        if not metadata:
            return {}

        keywords = metadata.keywords
        if keywords:
            keywords = ' '.join(k.code for k in keywords)
        else:
            keywords = ''

        return dict(search={
            'topic': metadata.ressort,
            'keywords': keywords,
        })


def _get(request, name, default=None):
    value = request.get(name, default)
    if value is default:
        return value
    value = value.strip()
    if value:
        return value
    return default

def search_form(request):
    g = lambda name, default=None: _get(request, name, default)
    fulltext = g('fulltext')
    from_ = parse_input_date(g('from', 'TT.MM.JJJJ'))
    until = parse_input_date(g('until', 'TT.MM.JJJJ'))
    volume, year = parse_volume_year(g('volume_year', 'WW/JJJJ'))
    topic = g('topic', None)
    authors = g('author', None)
    keywords = g('keywords', None)
    # four states: published, not-published, published-with-changes,
    # don't care (None)
    published = g('published', None)
    if not published:
        published = None
    types = request.get('types', [])
    return dict(
        fulltext=fulltext,
        from_=from_,
        until=until,
        volume=volume,
        year=year,
        topic=topic,
        authors=authors,
        keywords=keywords,
        published=published,
        types=types)

def form_query(request, filter_terms=None):
    form = search_form(request)
    if form is None:
        return None
    form['filter_terms'] = filter_terms
    return zeit.find.search.query(**form)

def get_favorites(request):
    favorites_id = u'Favoriten'
    clipboard = zeit.cms.clipboard.interfaces.IClipboard(request.principal)
    if not favorites_id in clipboard:
        clipboard.addClip(favorites_id)
    return clipboard[favorites_id]

class InputError(Exception):
    pass

class InputDateParseError(InputError):
    pass

def parse_input_date(s):
    """Given a date input string, return datetime.datetime object

    Date is of format DD.MM.YYYY. Special value 'TT.MM.JJJJ' is
    equivalent to no date at all.
    """
    s = s.strip()
    if not s:
        return None
    if s == 'TT.MM.JJJJ':
        return None
    try:
        day, month, year = s.split('.')
    except ValueError:
        raise InputDateParseError("Missing periods in date")
    try:
        day = int(day)
    except ValueError:
        raise InputDateParseError("Day is not a proper number")
    try:
        month = int(month)
    except ValueError:
        raise InputDateParseError("Month is not a proper number")
    try:
        year = int(year)
    except ValueError:
        raise InputDateParseError("Year is not a proper number")
    return datetime(year, month, day)

class VolumeYearError(InputError):
    pass

def parse_volume_year(s):
    """Parse volume/year indicator.

    Date is of format WW/JJJJ. Special value 'WW/JJJJ' is
    equivalent to no volume/year.
    """
    s = s.strip()
    if not s:
        return None, None
    if s == 'WW/JJJJ':
        return None, None
    try:
        volume, year = s.split('/')
    except ValueError:
        raise VolumeYearError("Missing / in volume.year")
    try:
        int(volume)
    except ValueError:
        raise VolumeYearError("Volume is not a proper number")
    try:
        int(year)
    except ValueError:
        raise VolumeYearError("Year is not a proper number")
    return volume, year

def format_date(dt):
    if dt is None:
        return ''
    return dt.strftime('%d.%m.%Y')

def format_amount(amount):
    if amount >= 1000:
        return "1000+"
    else:
        return str(amount)
