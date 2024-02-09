import argparse
import datetime
import itertools
import logging

import grokcore.component as grok
import lxml.builder
import requests
import zope.interface
import zope.lifecycleevent
import zope.schema

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish
import zeit.cms.cli
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.cms.workflow.dependency
import zeit.content.cp.interfaces
import zeit.content.infobox.interfaces
import zeit.content.portraitbox.interfaces
import zeit.content.volume.interfaces
import zeit.edit.interfaces
import zeit.retresco.interfaces
import zeit.retresco.search


log = logging.getLogger()
UNIQUEID_PREFIX = zeit.cms.interfaces.ID_NAMESPACE[:-1]


@zope.interface.implementer(zeit.content.volume.interfaces.IVolume, zeit.cms.interfaces.IAsset)
class Volume(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = """\
        <volume>
            <head/>
            <body/>
            <covers/>
        </volume>
    """

    zeit.cms.content.dav.mapProperties(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('date_digital_published', 'year', 'volume'),
    )

    _product_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(), zeit.workflow.interfaces.WORKFLOW_NS, 'product-id'
    )

    assets_to_publish = [
        zeit.content.portraitbox.interfaces.IPortraitbox,
        zeit.content.infobox.interfaces.IInfobox,
    ]

    @property
    def product(self):
        source = zeit.content.volume.interfaces.IVolume['product'].source(self)
        for value in source:
            if value.id == self._product_id:
                return value
        return None

    @product.setter
    def product(self, value):
        if self._product_id == value.id:
            return
        self._product_id = value.id if value is not None else None

    _teaserText = zeit.cms.content.dav.DAVProperty(
        zeit.content.volume.interfaces.IVolume['teaserText'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'teaserText',
    )

    @property
    def teaserText(self):
        text = self._teaserText
        if text is None:
            config = zope.app.appsetup.product.getProductConfiguration('zeit.content.volume')
            text = config['default-teaser-text']
        return self.fill_template(text)

    @teaserText.setter
    def teaserText(self, value):
        self._teaserText = value

    @property
    def teaserSupertitle(self):  # For display in CP-editor
        return self.fill_template('Ausgabe {name}/{year}')

    def fill_template(self, text):
        return self._fill_template(self, text)

    @staticmethod
    def _fill_template(context, text):
        if not text:
            return ''
        return text.format(year=context.year, name=str(context.volume).rjust(2, '0'))

    @property
    def _all_products(self):
        return [self.product] + self.product.dependent_products

    @property
    def previous(self):
        return self._find_in_order(None, self.date_digital_published, 'desc')

    @property
    def next(self):
        return self._find_in_order(self.date_digital_published, None, 'asc')

    def _find_in_order(self, start, end, sort):
        if len([x for x in [start, end] if x]) != 1:
            return None
        # Since `sort` is passed in accordingly, and we exclude ourselves,
        # the first result (if any) is always the one we want.
        query = {
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'doc_type': VolumeType.type}},
                        {'term': {'payload.workflow.product-id': self.product.id}},
                        {
                            'range': {
                                'payload.document.date_digital_published': zeit.retresco.search.date_range(  # noqa: E501
                                    start, end
                                )
                            }
                        },
                    ],
                    'must_not': [{'term': {'url': self.uniqueId.replace(UNIQUEID_PREFIX, '')}}],
                }
            },
            'sort': [{'payload.document.date_digital_published': sort}],
        }
        return Volume._find_via_elastic(query)

    @staticmethod
    def published_days_ago(days_ago):
        query = {
            'query': {
                'bool': {
                    'filter': [
                        {'term': {'doc_type': VolumeType.type}},
                        {'term': {'payload.workflow.published': True}},
                        {
                            'range': {
                                'payload.document.date_digital_published': {
                                    'gte': 'now-%dd/d' % (days_ago + 1),
                                    'lt': 'now-%dd/d' % days_ago,
                                }
                            }
                        },
                    ]
                }
            },
            'sort': [{'payload.workflow.date_last_published': 'desc'}],
        }
        return Volume._find_via_elastic(query)

    @staticmethod
    def _find_via_elastic(query):
        es = zope.component.getUtility(zeit.retresco.interfaces.IElasticsearch)
        result = es.search(query, rows=1)
        if not result:
            return None
        return zeit.cms.interfaces.ICMSContent(UNIQUEID_PREFIX + next(iter(result))['url'], None)

    def get_cover(self, cover_id, product_id=None, use_fallback=True):
        if product_id is None and use_fallback:
            product_id = self.product.id
        if product_id and product_id not in [prod.id for prod in self._all_products]:
            log.warning('%s is not a valid product id for %s' % (product_id, self))
            return None
        path = '//covers/cover[@id="{}" and @product_id="{}"]'.format(cover_id, product_id)
        node = self.xml.xpath(path)
        uniqueId = node[0].get('href') if node else None
        if uniqueId:
            return zeit.cms.interfaces.ICMSContent(uniqueId, None)
        if use_fallback:
            # Fall back to the main product (which must be self.product,
            # since we respond only to ids out of self._all_products)
            # Recursive call of this function with the main product ID
            return self.get_cover(cover_id, self.product.id, use_fallback=False)
        return None

    def set_cover(self, cover_id, product_id, imagegroup):
        if not self._is_valid_cover_id_and_product_id(cover_id, product_id):
            raise ValueError(
                'Cover id {} or product id {} are not ' 'valid.'.format(cover_id, product_id)
            )
        path = '//covers/cover[@id="{}" and @product_id="{}"]'.format(cover_id, product_id)
        node = self.xml.xpath(path)
        if node:
            self.xml.covers.remove(node[0])
        if imagegroup is not None:
            node = lxml.builder.E.cover(
                id=cover_id, product_id=product_id, href=imagegroup.uniqueId
            )
            self.xml.covers.append(node)
        super().__setattr__('_p_changed', True)

    def _is_valid_cover_id_and_product_id(self, cover_id, product_id):
        cover_ids = list(zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(self))
        product_ids = [prod.id for prod in self._all_products]
        return cover_id in cover_ids and product_id in product_ids

    def all_content_via_search(self, additional_query_constraints=None):
        """
        Get all content for this volume via ES.
        If u pass a list of additional query clauses, they will be added as
        an AND-operand to the query.
        """
        if not additional_query_constraints:
            additional_query_constraints = []
        elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        query = [
            {'term': {'payload.document.year': self.year}},
            {'term': {'payload.document.volume': self.volume}},
            {
                'bool': {
                    'should': [
                        {'term': {'payload.workflow.product-id': x.id}} for x in self._all_products
                    ]
                }
            },
            {
                'bool': {
                    'must_not': {'term': {'payload.document.channels': 'zeit-magazin wochenmarkt'}}
                }
            },
        ]

        result = elastic.search(
            {
                'query': {
                    'bool': {
                        'filter': query + additional_query_constraints,
                        'must_not': [{'term': {'url': self.uniqueId.replace(UNIQUEID_PREFIX, '')}}],
                    }
                }
            },
            rows=1000,
        )
        # We assume a maximum content amount per usual production print volume
        assert result.hits < 250
        content = []
        for item in result:
            item = zeit.cms.interfaces.ICMSContent(UNIQUEID_PREFIX + item['url'], None)
            if item is not None:
                content.append(item)
        return content

    def change_contents_access(
        self,
        access_from,
        access_to,
        published=True,
        exclude_performing_articles=True,
        dry_run=False,
    ):
        constraints = [{'term': {'payload.document.access': access_from}}]
        if exclude_performing_articles:
            try:
                to_filter = _find_performing_articles_via_webtrekk(self)
            except Exception:
                log.error('Error while retrieving data from webtrekk api', exc_info=True)
                return []

            log.info('Not changing access for %s ' % to_filter)
            filter_constraint = {'bool': {'must_not': {'terms': {'url': to_filter}}}}
            constraints.append(filter_constraint)
        if published:
            constraints.append({'term': {'payload.workflow.published': True}})
        cnts = self.all_content_via_search(constraints)
        if dry_run:
            return cnts
        for cnt in cnts:
            try:
                with zeit.cms.checkout.helper.checked_out(cnt) as co:
                    co.access = access_to
                    zope.lifecycleevent.modified(
                        co,
                        zope.lifecycleevent.Attributes(
                            zeit.cms.content.interfaces.ICommonMetadata, 'access'
                        ),
                    )
            except Exception:
                log.error("Couldn't change access for {}. Skipping " 'it.'.format(cnt.uniqueId))
        return cnts

    def content_with_references_for_publishing(self):
        additional_constraints = [
            {'term': {'doc_type': zeit.content.article.article.ArticleType.type}},
            {'term': {'payload.workflow.published': False}},
            {'term': {'payload.workflow.urgent': True}},
        ]
        articles_to_publish = self.all_content_via_search(
            additional_query_constraints=additional_constraints
        )
        # Flatten the list of lists and remove duplicates
        articles_with_references = list(
            set(
                itertools.chain.from_iterable(
                    [self._with_references(article) for article in articles_to_publish]
                )
            )
        )
        articles_with_references.append(self)
        return articles_with_references

    def _with_references(self, article):
        """
        :param content: CMSContent
        :return: [referenced_content1, ..., content]
        """
        # XXX Using zeit.cms.relation.IReferences would make sense here as
        # well but due to some license issues with images referenced by
        # articles we have to be careful what we want to publish
        with_dependencies = [
            content
            for content in zeit.edit.interfaces.IElementReferences(article, [])
            if self._needs_publishing(content)
        ]
        with_dependencies.append(article)
        return with_dependencies

    def _needs_publishing(self, content):
        # Dont publish content which is already published
        if zeit.cms.workflow.interfaces.IPublishInfo(content).published:
            return False
        # content has to provide one of interfaces defined above
        return any(x.providedBy(content) for x in self.assets_to_publish)


class VolumeType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Volume
    interface = zeit.content.volume.interfaces.IVolume
    title = _('Volume')
    type = 'volume'


@grok.implementer(zeit.cms.content.interfaces.ICommonMetadata)
class VolumeMetadata(grok.Adapter):
    """Since ICenterPage inherits from ICommonMetadata, we need to ensure
    that adapting a volume to ICommonMetadata returns fields from the volume,
    and not the CP.
    """

    grok.context(zeit.content.volume.interfaces.IVolume)

    missing = object()

    def __getattr__(self, name):
        value = getattr(self.context, name, self.missing)
        if value is self.missing:
            field = zeit.cms.content.interfaces.ICommonMetadata.get(name, None)
            return field.default
        return value


@grok.adapter(zeit.content.volume.interfaces.IVolume)
@grok.implementer(zeit.cms.workflow.interfaces.IPublishPriority)
def publish_priority_volume(context):
    # XXX Kludgy. The JS-based "do-publish-all" uses the context's priority to
    # retrieve the task queue where it looks up the job id, and
    # publish_multiple runs with PRIORITY_LOW (which makes sense). To connect
    # these two, we set IVolume to low, even though that's not really
    # warrantend, semantically speaking.
    return zeit.cms.workflow.interfaces.PRIORITY_LOW


class CoverDependency(zeit.cms.workflow.dependency.DependencyBase):
    """
    If a Volume is published, its covers are published as well.
    """

    grok.context(zeit.content.volume.interfaces.IVolume)
    grok.name('zeit.content.volume.cover')

    retract_dependencies = True

    def get_dependencies(self):
        cover_names = zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(self.context)
        covers = []
        for product in self.context._all_products:
            for cover_name in cover_names:
                cover = self.context.get_cover(
                    cover_name, product_id=product.id, use_fallback=False
                )
                if cover:
                    covers.append(cover)
        return covers


@grok.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@grok.implementer(zeit.content.volume.interfaces.IVolume)
def retrieve_volume_using_info_from_metadata(context):
    if context.year is None or context.volume is None or context.product is None:
        return None

    unique_id = None
    if context.product.volume and context.product.location:
        unique_id = Volume._fill_template(context, context.product.location)
    else:
        main_product = zeit.content.volume.interfaces.PRODUCT_SOURCE(context).find(
            context.product.relates_to
        )
        if main_product and main_product.volume and main_product.location:
            unique_id = Volume._fill_template(context, main_product.location)
    return zeit.cms.interfaces.ICMSContent(unique_id, None)


@grok.adapter(zeit.content.volume.interfaces.IVolume)
@grok.implementer(zeit.content.cp.interfaces.ICenterPage)
def retrieve_corresponding_centerpage(context):
    if context.product is None:
        return None

    unique_id = None
    if context.product.location:
        unique_id = context.fill_template(context.product.centerpage)
    else:
        main_product = zeit.content.volume.interfaces.PRODUCT_SOURCE(context).find(
            context.product.relates_to
        )
        if main_product and main_product.centerpage:
            unique_id = context.fill_template(main_product.centerpage)
    cp = zeit.cms.interfaces.ICMSContent(unique_id, None)
    if not zeit.content.cp.interfaces.ICenterPage.providedBy(cp):
        return None
    return cp


def _find_performing_articles_via_webtrekk(volume):
    """
    Check webtrekk-API for performing articles. Since the webtrekk api,
    this should only be used when performance is no criteria.
    """
    api_date_format = '%Y-%m-%d %H:%M:%S'
    cr_metric_name = 'CR Bestellungen Abo (Artikelbasis)'
    order_metric_name = 'Anzahl Bestellungen mit Seitenbezug'
    config = zope.app.appsetup.product.getProductConfiguration('zeit.content.volume')
    info = zeit.cms.workflow.interfaces.IPublishInfo(volume)
    start = info.date_first_released
    stop = start + datetime.timedelta(weeks=3)
    # XXX Unfortunately the webtrekk api doesn't allow filtering for custom
    # metrics, so we got filter our results here
    body = {
        'version': '1.1',
        'method': 'getAnalysisData',
        'params': {
            'login': config['access-control-webtrekk-username'],
            'pass': config['access-control-webtrekk-password'],
            'customerId': config['access-control-webtrekk-customerid'],
            'language': 'de',
            'analysisConfig': {
                'analysisFilter': {
                    'filterRules': [
                        {
                            'objectTitle': 'cp30 - Wall-Status',
                            'comparator': '=',
                            'filter': 'paid',  # Only paid articles
                            'scope': 'page',
                        },
                    ]
                },
                'metrics': [
                    {'sortOrder': 'desc', 'title': order_metric_name},
                    {'sortOrder': 'desc', 'title': cr_metric_name},
                ],
                'analysisObjects': [{'title': 'Seiten'}],
                'startTime': start.strftime(api_date_format),
                'stopTime': stop.strftime(api_date_format),
                'rowLimit': 1000,
                'hideFooters': 1,
            },
        },
    }

    access_control_config = zeit.content.volume.interfaces.ACCESS_CONTROL_CONFIG
    resp = requests.post(
        config['access-control-webtrekk-url'],
        timeout=int(config['access-control-webtrekk-timeout']),
        json=body,
    )
    result = resp.json()
    if result.get('error'):
        raise Exception('Webtrekk API reported an error %s' % result.get('error'))
    data = result['result']['analysisData']
    urls = set()
    for page, order, cr in data:
        url = page.split('zeit.de/')[1]
        if (volume.fill_template('{year}/{name}') in url) and (
            float(cr) >= access_control_config.min_cr
            or int(order) >= access_control_config.min_orders
        ):
            urls.add('/' + url)
    return list(urls)


@zeit.cms.cli.runner(
    principal=zeit.cms.cli.from_config('zeit.content.volume', 'access-control-principal')
)
def change_access():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days-ago', type=int, help='Select volume that was published x days ago.')
    parser.add_argument('--uniqueid', help='Select volume by uniqueId.')
    parser.add_argument(
        '--dry-run', help="Don't actually perform access change", action='store_true'
    )
    options = parser.parse_args()

    if bool(options.days_ago) == bool(options.uniqueid):
        parser.error('You have to specify either uniqueid or days-ago')

    if not options.uniqueid:
        try:
            options.uniqueid = Volume.published_days_ago(options.days_ago)
        except Exception:
            log.error('Error while searching for volume', exc_info=True)

    if not options.uniqueid:
        log.info("Didn't find any volumes which need changes.")
        return
    volume = zeit.cms.interfaces.ICMSContent(options.uniqueid)
    log.info('Processing %s', volume.uniqueId)
    content = volume.change_contents_access('abo', 'registration', dry_run=options.dry_run)
    content.extend(
        volume.change_contents_access('dynamic', 'registration', dry_run=options.dry_run)
    )
    if options.dry_run:
        log.info('Access would be changed for %s' % content)
        return
    IPublish(volume).publish_multiple(content, background=False)
