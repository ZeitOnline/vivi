# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import itertools
from datetime import datetime, timedelta
import cjson
import pysolr
import zeit.cms.browser.view
import zc.resourcelibrary
import zope.component
import zope.interface
import zope.app.appsetup.product
import zope.viewlet.interfaces
import zeit.cms.interfaces
import zeit.cms.clipboard.interfaces
import zeit.cms.content.interfaces
import zeit.cms.browser.interfaces
import zeit.cms.browser.preview
import zc.iso8601.parse
from zeit.find import lucenequery as lq

def resources(request):
    return zope.component.getAdapter(
        request, zope.interface.Interface, name='zeit.find')

def get_solr():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.find')
    solr_url = config.get('solr_url')
    return pysolr.Solr(solr_url)

class Find(zeit.cms.browser.view.Base):

    def __call__(self):
        zc.resourcelibrary.need('zeit.find')
        return super(Find, self).__call__()

class JSONView(zeit.cms.browser.view.Base):
    template = None

    def __init__(self, context, request):
        super(JSONView, self).__init__(context, request)
        self.resources = resources(request)

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/json')
        result = self.json()

        # use template indicated in JSON if it's there,
        # otherwise use class template
        template = result.pop('template', None)
        if template is None:
            template = self.template
        if template is not None:
            result['template_url'] = self.resources[template]()
        return cjson.encode(result)

    def json(self):
        return {}

    def url(self, view, uniqueId):
        return super(JSONView, self).url(
            self.context, '%s?uniqueId=%s' % (view, uniqueId))

class SearchForm(JSONView):
    template = 'search_form.jsont'
    
class SearchResult(JSONView):
    template = 'search_result.jsont'
    
    def sort_order(self):
        return self.request.get('sort_order', 'relevance')    
    
    def json(self):
        q = search_form_query(self.request)
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

        result_fields = ['uniqueId', 'published',
                         'teaser_title', 'teaser_text',
                         'last-semantic-change', 'ressort',
                         'authors']

        sort_order = self.request.get('sort_order', 'score desc')
        if sort_order == 'relevance':
            sort_order = 'score desc'
        elif sort_order == 'date':
            sort_order = 'last-semantic-change desc'

        r = self.resources
        results = []
        conn = get_solr()

        for result in conn.search(q,
                                  sort=sort_order,
                                  fl=' '.join(result_fields)):
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

            published = result.get('published', True)
            if published:
                publication_status = r['published.png']()
            else:
                publication_status = r['unpublished.png']()

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
                    'author': result.get('authors', ''),
                    'author_filter': '',
                    'related_url': self.url('expanded_search_result', uniqueId),
                    'favorite_url': self.url('toggle_favorited', uniqueId),
                    })
        if not results:
            return {'template': 'no_search_result.jsont'}
        return {'results': results}

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
    # three states: want all published, want all unpublished, don't care
    published = g('published', None)
    if published == 'published':
        published = True
    elif published == 'unpublished':
        published = False
    else:
        published = None
    types = set()
    for t in ['article', 'gallery', 'video', 'teaser', 'centerpage']:
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

def search_query(fulltext, from_, until, topic, authors, keywords,
                 published, types, filter_terms=None):
    """Given parameters, create solr query string.
    """
    filter_terms = filter_terms or []
    
    terms = []
    terms.append(lq.field('text', fulltext))
    if from_ is not None or until is not None:
        terms.append(
            lq.datetime_range('last-semantic-change', from_, until))
    if topic is not None:
        terms.append(lq.field('ressort', topic))
    if authors is not None:
        terms.append(lq.multi_field('authors', authors))
    if keywords is not None:
        terms.append(lq.multi_field('keywords', keywords))
    if published is not None:
        terms.append(lq.bool_field('published', published))

    terms.extend(filter_terms)
    return lq.and_(*terms)

def search_form_query(request, filter_terms=None):
    form = search_form(request)
    if form is None:
        return None
    form['filter_terms'] = filter_terms
    return search_query(**form)

class ExtendedSearchForm(JSONView):
    template = 'extended_search_form.jsont'

class ResultFilters(JSONView):
    template = 'result_filters.jsont'

    
    def time_entries(self):
        conn = get_solr()
        result = []
        for name, filter in [("heute", today_filter),
                             ("gestern", yesterday_filter),
                             ("7 Tage",  seven_day_filter),
                             ("letzter Monat", month_filter),
                             ("letztes halbes Jahr", half_year_filter),
                             ("letztes Jahr", year_filter)]:
            q = search_form_query(self.request, filter_terms=[filter()])
            amount = conn.search(q, rows=0).hits
            if amount > 0:
                result.append(dict(title=name,
                                   amount=format_amount(amount),
                                   query=""))
        return result
    
    def author_entries(self):
        return [{"title": "Martijn Faassen", "amount": "45", "query": ""},
                {"title": "Christian Zagrodnick", "amount": "124", "query": ""}]

    def json(self):
        conn = get_solr()
        q = search_form_query(self.request)
        facets = {
            'facet': 'true',
            'facet.field': ['ressort', 'type'],
            }
        facet_data = conn.search(q, rows=0, **facets).facets
        facet_fields = facet_data['facet_fields']
        return {"results": [
                {"row": [{"title": "Ressort",
                          "entries": _entries(facet_fields['ressort'])},
                         {"title": "Zeit",
                          "entries": self.time_entries()},
                         ]},
                {"row": [{"title": "Inhaltstyp",
                          "entries": _entries(facet_fields['type'])},
                         {"title": "Autor",
                          "entries": self.author_entries()},
                 ]}]}
    

def _entries(counts):
    counts = sorted(grouper(2, counts))
    result = []
    for title, amount in counts:
        if amount == 0:
            continue
        result.append(
            dict(title=title,
                 amount=format_amount(amount),
                 query=''))
    return result

def today_filter():
    start = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return lq.datetime_range('last-semantic-change', start, end)

def yesterday_filter():
    start = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    end = start + timedelta(days=1)
    return lq.datetime_range('last-semantic-change', start, end)

def seven_day_filter():
    end = datetime.now()
    start = end - timedelta(days=7)
    return lq.datetime_range('last-semantic-change', start, end)

def month_filter():
    end = datetime.now()
    # XXX last month period if 31 days?
    start = end - timedelta(days=31)
    return lq.datetime_range('last-semantic-change', start, end)

def half_year_filter():
    end = datetime.now()
    # last half year, about 183 days
    start = end - timedelta(days=183)
    return lq.datetime_range('last-semantic-change', start, end)

def year_filter():
    end = datetime.now()
    # last year, about 366 days (to be on the safe side)
    start = end - timedelta(days=366)
    return lq.datetime_range('last-semantic-change', start, end)

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

def get_favorites(request):
    favorites_id = u'Favoriten'
    clipboard = zeit.cms.clipboard.interfaces.IClipboard(request.principal)
    if not favorites_id in clipboard:
        clipboard.addClip(favorites_id)
    return clipboard[favorites_id]

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

def grouper(n, iterable, padvalue=None):
    return itertools.izip(
        *[itertools.chain(iterable, itertools.repeat(padvalue, n-1))]*n)
