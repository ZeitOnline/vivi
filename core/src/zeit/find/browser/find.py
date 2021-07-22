import datetime
import logging
import pendulum
import six
import six.moves.urllib.parse
import zeit.cms.browser.view
import zeit.cms.clipboard.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.find.interfaces
import zeit.find.search
import zope.browser.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.i18n
import zope.session.interfaces


log = logging.getLogger(__name__)


class JSONView(zeit.cms.browser.view.JSON):

    resource_library = 'zeit.find'

    def url(self, view, uniqueId):
        return super(JSONView, self).url(
            self.context, '%s?uniqueId=%s' % (view, uniqueId))


class SearchForm(JSONView):

    template = 'search_form.jsont'

    def json(self):
        metadata_if = zeit.cms.content.interfaces.ICommonMetadata
        return dict(
            access=self.get_source(metadata_if['access'].source,
                                   'access', 'access_title'),
            products=self.products,
            ressorts=self.get_source(metadata_if['ressort'].source,
                                     'ressort', 'ressort_name'),
            series=self.series,
            types=self.types,
        )

    def get_source(self, source, value_name, title_name):
        # XXX wrong if some of these sources should become context-dependent
        source = source(None)
        result = []
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.browser.interfaces.ITerms)
        for value in source:
            title = terms.getTerm(value).title
            result.append({
                value_name: value,
                title_name: title})
        return result

    @property
    def products(self):
        metadata_if = zeit.cms.content.interfaces.ICommonMetadata
        result = self.get_source(metadata_if['product'].source,
                                 'product_id', 'product_name')
        for entry in result:
            entry['product_id'] = entry['product_id'].id
        return result

    @property
    def series(self):
        metadata_if = zeit.cms.content.interfaces.ICommonMetadata
        result = self.get_source(metadata_if['serie'].source,
                                 'serie', 'serie_title')
        for entry in result:
            entry['serie'] = entry['serie'].serienname
        return result

    CONTENT_TYPES = [
        'advertisement',
        'article',
        'author',
        'centerpage-2009',
        'embed',
        'gallery',
        'image-group',
        'infobox',
        'link',
        'playlist',
        'portraitbox',
        'rawxml',
        'video',
        'volume'
    ]

    @property
    def types(self):
        result = []
        for name in self.CONTENT_TYPES:
            typ = zope.component.queryUtility(
                zeit.cms.interfaces.ITypeDeclaration, name=name)
            if typ is None:
                # Should happen only in tests that don't have much ZCML loaded.
                continue
            result.append({
                'title': zope.i18n.translate(
                    typ.title or typ.type, context=self.request),
                'type': typ.type,
            })
        return sorted(result, key=lambda r: r['title'])


def get_favorited_css_class(favorited):
    return 'toggle_favorited ' + (
        'favorited' if favorited else 'not_favorited')


class DottedNestedDict(object):

    def __init__(self, dict_):
        self.dict = dict_

    def get(self, key, default=None):
        dict_ = self.dict
        while '.' in key:
            prefix, _, rest = key.partition('.')
            if prefix in dict_:
                dict_ = dict_[prefix]
                key = rest
            else:
                break
        if key not in dict_:
            log.debug('key "%s" not found', key)
        return dict_.get(key, default)


class SearchResult(JSONView):

    template = 'search_result.jsont'

    search_result_keys = (
        'application_url',
        'authors',
        'date',
        'favorite_url',
        'favorited',
        'favorited_css_class',
        'graphical_preview_url',
        'icon',
        'product',
        'publication_status',
        'serie',
        'subtitle',
        'supertitle',
        'teaser_text',
        'teaser_title',
        'topic',
        'type',
        'uniqueId',
    )

    def results(self, results):
        processed = []
        for result in results:
            entry = {}
            result = DottedNestedDict(result)
            for key in self.search_result_keys:
                handler = getattr(self, 'get_%s' % key)
                value = handler(result)
                if isinstance(value, int) and not isinstance(value, bool):
                    value = six.text_type(value)
                entry[key] = value
            processed.append(entry)
        if not processed:
            return {'template': 'no_search_result.jsont'}
        return {'results': processed}

    def json(self):
        try:
            q = form_query(self.request)
            q['sort'] = self.sort_order()
        except InputError as e:
            error = six.text_type(e)
            return {'template': 'no_search_result.jsont', "error": error}
        if q is None:
            return {'template': 'no_search_result.jsont'}
        self.store_session()
        elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        try:
            results = elastic.search(q)
            return self.results(results)
        except Exception as e:
            return {'template': 'no_search_result.jsont',
                    'error': e.args[0]}

    SORT_ORDERS = {
        'date': [{'payload.document.last-semantic-change': 'desc'}],
        'relevance': ['_score'],
    }

    def sort_order(self):
        return self.SORT_ORDERS[self.request.get('sort_order', 'relevance')]

    def store_session(self):
        session = zope.session.interfaces.ISession(self.request)['zeit.find']
        parameters = search_parameters(self.request)
        if session.get('last-query') != parameters:
            session['last-query'] = parameters

    def get_first_field(self, result, *fields):
        for field in fields:
            value = result.get(field)
            if value:
                return value
        return ''

    # generic processors

    def get_application_url(self, result=None):
        return self.request.getApplicationURL()

    def get_date(self, result):
        return format_date(self._get_unformatted_date(result))

    def get_favorite_url(self, result):
        return self.url('toggle_favorited', self.get_uniqueId(result))

    def get_favorited_css_class(self, result):
        return get_favorited_css_class(self.get_favorited(result))

    def get_product(self, result):
        source = zeit.cms.content.interfaces.ICommonMetadata['product'].source(
            None)
        product = source.find(result.get('payload.workflow.product-id'))
        return product and product.title or ''

    def get_publication_status(self, result):
        r = self.resource_url
        published = self._get_unformatted_publication_status(result)
        if published == 'published':
            publication_status = r('published.png')
        elif published == 'published-with-changes':
            publication_status = r('published_new.png')
        else:
            publication_status = r('unpublished.png')
        return publication_status

    def get_teaser_title(self, result):
        return self.get_first_field(
            result, 'payload.teaser.title', 'payload.body.title', 'url')

    def get_type(self, result):
        return result.get('doc_type', '')

    def get_authors(self, result):
        return result.get('payload.document.author', [])

    def _get_unformatted_date(self, result):
        last_semantic_change = result.get(
            'payload.document.last-semantic-change')
        dt = None
        if last_semantic_change is not None:
            dt = pendulum.parse(last_semantic_change)
        return dt

    def get_favorited(self, result):
        return self.get_uniqueId(result) in self.favorite_ids

    def get_graphical_preview_url(self, result):
        url = result.get('payload.vivi.cms_preview_url')
        if not url:
            return None
        url_p = six.moves.urllib.parse.urlsplit(url)
        if url_p.scheme == '':
            url = self.get_application_url() + url
        return url

    def get_icon(self, result):
        icon = result.get('payload.vivi.cms_icon')
        if icon:
            icon = self.get_application_url() + icon
        return icon

    def _get_unformatted_publication_status(self, result):
        return result.get('payload.vivi.publish_status', 'published')

    def get_subtitle(self, result):
        return result.get('payload.body.subtitle', '')

    def get_supertitle(self, result):
        return self.get_first_field(
            result, 'payload.teaser.supertitle', 'payload.body.supertitle')

    def get_teaser_text(self, result):
        return self.get_first_field(
            result, 'payload.teaser.text', 'payload.body.text')

    def get_serie(self, result):
        return result.get('payload.document.serie', '')

    def get_topic(self, result):
        return result.get('payload.document.ressort', '')

    def get_uniqueId(self, result):
        url = result.get('url', '')
        return zeit.cms.interfaces.ID_NAMESPACE.rstrip('/') + url

    @zope.cachedescriptors.property.Lazy
    def favorite_ids(self):
        """Record any known favorites.

        This isn't that pleasant to do every search, but we need to match the
        uniqueIds quickly during the search results. Besides there are not so
        many favorites anyway.

        """
        favorite_uniqueIds = set()
        for favorite in get_favorites(self.request).values():
            if not zeit.cms.clipboard.interfaces.IObjectReference.providedBy(
                    favorite):
                continue
            uniqueId = favorite.referenced_unique_id
            if not uniqueId:
                continue
            favorite_uniqueIds.add(uniqueId)
        return favorite_uniqueIds


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


class LastQuery(JSONView):

    def json(self):
        last_query = {}
        session = zope.session.interfaces.ISession(self.request).get(
            'zeit.find')
        if session is not None:
            last_query = session.get('last-query', {})
        query = {}
        for key, value in last_query.items():
            if isinstance(value, list):
                key = '%s:list' % key
            query[key] = value
        return query


def _get(request, name, default=None):
    value = request.get(name, default)
    if value is default:
        return value
    value = value.strip()
    if value:
        return value
    return default


def search_parameters(request):
    """extract the search parameters from the request in raw form"""

    parameters = [
        'access',
        'author',
        'extended_search_expanded',
        'from',
        'fulltext',
        'keywords',
        'raw-tags',
        'product',
        'published',
        'result_filters_expanded',
        'serie',
        'sort_order',
        'topic',
        'type_search_expanded',
        'until',
        'volume',
        'year',
    ]

    result = {}
    for name in parameters:
        result[name] = _get(request, name)
    result['types'] = request.get('types', [])
    return result


def search_form(request):
    """extract the search parameters from the request in a format suitable
    to build a search query"""

    def g(name, default=None):
        return _get(request, name, default)
    fulltext = g('fulltext')
    from_ = parse_input_date(g('from', 'TT.MM.JJJJ'))
    until = parse_input_date(g('until', 'TT.MM.JJJJ'))
    volume, year = parse_volume_year(g('volume_year', 'WW/JJJJ'))
    topic = g('topic', None)
    access = g('access', None)
    authors = g('author', None)
    keywords = g('keywords', None)
    raw_tags = g('raw-tags', None)
    product_id = g('product', None)
    show_news = g('show_news', False)
    serie = g('serie', None)
    # four states: published, not-published, published-with-changes,
    # don't care (None)
    published = g('published', None)
    if not published:
        published = None
    types = request.get('types', [])
    if 'embed' in types:
        types.append('text')  # BBB ZON-2932
    return dict(
        access=access,
        authors=authors,
        from_=from_,
        fulltext=fulltext,
        keywords=keywords,
        raw_tags=raw_tags,
        product_id=product_id,
        published=published,
        serie=serie,
        show_news=show_news,
        topic=topic,
        types=types,
        until=until,
        volume=volume,
        year=year,
    )


def form_query(request, filter_terms=None):
    form = search_form(request)
    if form is None:
        return None
    form['filter_terms'] = filter_terms
    return zeit.find.search.query(**form)


def get_favorites(request):
    favorites_id = u'Favoriten'
    clipboard = zeit.cms.clipboard.interfaces.IClipboard(request.principal)
    if favorites_id not in clipboard:
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
    return datetime.datetime(year, month, day)


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
