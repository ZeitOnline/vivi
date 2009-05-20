# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime
import zeit.cms.browser.view
import zc.resourcelibrary
import zope.component
import zope.interface
import zope.viewlet.interfaces
import zeit.cms.interfaces
import zeit.cms.clipboard.interfaces
import zeit.cms.content.interfaces
import zeit.cms.browser.interfaces
import zeit.cms.browser.preview
import zc.iso8601.parse
import zeit.find.search



class Find(zeit.cms.browser.view.Base):
    def __call__(self):
        zc.resourcelibrary.need('zeit.find')
        return super(Find, self).__call__()


class JSONView(zeit.cms.browser.view.JSON):

    resource_library = 'zeit.find'


class SearchForm(JSONView):

    template = 'search_form.jsont'
    
class SearchResult(JSONView):
    template = 'search_result.jsont'
    
    def sort_order(self):
        return self.request.get('sort_order', 'relevance')    
    
    def json(self):
        q = form_query(self.request)
        if q is None:
            return {"results":[]}

        # record any known favorites
        # XXX this isn't that pleasant to do every search,
        # but we need to match the uniqueIds quickly during
        # the search results
        favorite_uniqueIds = set()
        for favorite in get_favorites(self.request).values():
            uniqueId = favorite.references.uniqueId
            if not uniqueId:
                continue
            favorite_uniqueIds.add(uniqueId)

        r = self.resources
        results = []        
        for result in zeit.find.search.search(q, self.sort_order()):
            uniqueId = result.get('uniqueId', '')
            if uniqueId in favorite_uniqueIds:
                favorited_icon = r['favorite.png']()
            else:
                favorited_icon = r['not_favorite.png']()
            
            last_semantic_change = result.get('last-semantic-change')
            if last_semantic_change is not None:
                dt = zc.iso8601.parse.datetimetz(result['last-semantic-change'])
            else:
                dt = None

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
    
            preview_url = zeit.cms.browser.preview.get_preview_url(
                'preview-prefix', uniqueId)
            
            results.append({
                    'uniqueId': uniqueId,
                    'icon': '/@@/zeit-content-article-interfaces-IArticle-zmi_icon.png',
                    'favorited': favorited_icon,
                    'publication_status': publication_status,
                    'arrow': r['arrow_right.png'](),
                    'teaser_title': result.get('teaser_title', ''),
                    'teaser_text': result.get('teaser_text', ''),
                    'preview_url': preview_url,
                    'date': format_date(dt),
                    'date_filter': '',
                    'week': format_week(dt),
                    'week_filter': '',
                    'topics': result.get('ressort', ''),
                    'topics_filter': '',
                    'author': ' '.join(result.get('authors', [])),
                    'author_filter': '',
                    'related_url': self.url('expanded_search_result', uniqueId),
                    'favorite_url': self.url('toggle_favorited', uniqueId),
                    })
        if not results:
            return {'template': 'no_search_result.jsont'}
        return {'results': results}


class ExtendedSearchForm(JSONView):
    template = 'extended_search_form.jsont'


class ResultFilters(JSONView):
    template = 'result_filters.jsont'

    def json(self):
        q = form_query(self.request)
        (time_counts, topic_counts,
         author_counts, type_counts) = zeit.find.search.counts(q)

        return {"results": [
                {"row": [{"title": "Ressort",
                          "entries": _entries(topic_counts)},
                         {"title": "Zeit",
                          "entries": _entries(time_counts)}
                         ]},
                {"row": [{"title": "Inhaltstyp",
                          "entries": _entries(type_counts)},
                         {"title": "Autor",
                          "entries": _entries(author_counts)},
                         ]},
                ]}

def _entries(counts):
    result = []
    for name, count in counts:
        result.append(dict(title=name,
                           amount=format_amount(count),
                           query=''))
    return result


class ExpandedSearchResult(JSONView):
    template = 'expanded_search_result.jsont'

    def json(self):
        uniqueId = self.request.get('uniqueId')
        if not uniqueId:
            return {'template': 'no_expanded_search_result.jsont'}
        
        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        related = zeit.cms.related.interfaces.IRelatedContent(content).related

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
        r = self.resources
        content = zeit.cms.interfaces.ICMSContent(
            self.request.get('uniqueId'))

        favorites = get_favorites(self.request)
        if content.__name__ in favorites:
            del favorites[content.__name__]
            return {'favorited': r['not_favorite.png']()}
        favorites[content.__name__] = (zeit.cms.clipboard.
                                       interfaces.IClipboardEntry(content))
        return {'favorited': r['favorite.png']()}

class Favorites(JSONView):
    template = 'search_result.jsont'

    def result_entry(self, content):
        r = self.resources
        uniqueId = content.uniqueId
        favorited_icon = r['favorite.png']()

        metadata = zeit.cms.content.interfaces.ICommonMetadata(content, None)

        if metadata:
            if metadata.authors:
                authors = ' '.join(metadata.authors)
            else:
                authors = ''
        else:
            authors = ''
            
        return {
            'uniqueId': uniqueId,
            'icon': '/@@/zeit-content-article-interfaces-IArticle-zmi_icon.png',
            'favorited': favorited_icon,
            'publication_status': r['published.png'](),
            'arrow': r['arrow_right.png'](),
            'teaser_title': (metadata.teaserTitle or '') if metadata else '',
            'teaser_text': (metadata.teaserText or '') if metadata else '',
            'preview_url': '',
            'date': '13.02.2009',
            'date_filter': '',
            'week': '13/2009',
            'week_filter': '',
            'topics': 'Politik',
            'topics_filter': '',
            'author': authors,
            'author_filter': '',
            'related_url': self.url('expanded_search_result', uniqueId),
            'favorite_url': self.url('toggle_favorited', uniqueId),
            }

    def json(self):
        favorites = get_favorites(self.request)
        return {"results": [
            self.result_entry(a) for a in [
                zeit.cms.interfaces.ICMSContent(c.referenced_unique_id)
                for c in favorites.values()]]}
    
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
    if fulltext is None:
        return None
    from_ = parse_input_date(g('from', 'TT.MM.JJJJ'))
    until = parse_input_date(g('until', 'TT.MM.JJJJ'))
    topic = g('topic', None)
    authors = g('author', None)
    keywords = g('keywords', None)
    # four states: published, not-published, published-with-changes,
    # don't care (None)
    published = g('published', None)
    if not published:
        published = None
    # detect whether we are looking for expanded results or not
    expanded = g('from', None) is not None
    if not expanded:
        types = zeit.find.search.TYPES
    else:
        types = set()
        for t in zeit.find.search.TYPES:
            if g(t, '') == 'on':
                types.add(t)
    return dict(
        fulltext=fulltext,
        from_=from_,
        until=until,
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

class InputDateParseError(Exception):
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

def format_date(dt):
    if dt is None:
        return ''
    return dt.strftime('%d.%m.%Y')

def format_week(dt):
    if dt is None:
        return ''
    iso_year, iso_week, iso_weekday = dt.isocalendar()
    return '%s/%s' % (iso_week, iso_year)

def format_amount(amount):
    if amount >= 1000:
        return "1000+"
    else:
        return str(amount)
