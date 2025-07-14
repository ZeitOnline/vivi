import argparse
import datetime

from sqlalchemy import bindparam, select
from sqlalchemy import text as sql
import grokcore.component as grok
import lxml.builder
import opentelemetry.trace
import pendulum
import requests
import zope.component
import zope.interface
import zope.lifecycleevent
import zope.schema

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish
from zeit.connector.models import Content as ConnectorModel
import zeit.cms.cli
import zeit.cms.config
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.cms.workflow.dependency
import zeit.content.cp.interfaces
import zeit.content.infobox.interfaces
import zeit.content.portraitbox.interfaces
import zeit.content.volume.interfaces
import zeit.edit.interfaces
import zeit.retresco.interfaces
import zeit.retresco.search


UNIQUEID_PREFIX = zeit.cms.interfaces.ID_NAMESPACE[:-1]


@zope.interface.implementer(zeit.content.volume.interfaces.IVolume, zeit.cms.interfaces.IAsset)
class Volume(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = """\
        <volume>
            <head/>
            <body/>
            <title-overrides/>
            <covers/>
        </volume>
    """

    zeit.cms.content.dav.mapProperties(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('date_digital_published', 'year', 'volume', 'title', 'teaser', 'background_color'),
    )

    _product_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(), zeit.workflow.interfaces.WORKFLOW_NS, 'product-id'
    )

    assets_to_publish = [
        zeit.content.portraitbox.interfaces.IPortraitbox,
        zeit.content.infobox.interfaces.IInfobox,
    ]

    @property
    def repository(self):
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

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

    _volume_note = zeit.cms.content.dav.DAVProperty(
        zeit.content.volume.interfaces.IVolume['volume_note'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'volume_note',
    )

    @property
    def volume_note(self):
        text = self._volume_note
        if text is None:
            text = zeit.cms.config.required('zeit.content.volume', 'default-teaser-text')
        return self.fill_template(text)

    @volume_note.setter
    def volume_note(self, value):
        self._volume_note = value

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
        return self.find_in_order('DESC')

    @property
    def next(self):
        return self.find_in_order('ASC')

    def find_in_order(self, order):
        cmp_op = '>' if order == 'ASC' else '<'
        sql_query = f"""
        type = 'volume'
        AND product = :product
        AND volume_date_digital_published {cmp_op} :date_digital_published
        ORDER BY volume_date_digital_published {order}
        LIMIT 1
        """

        query = select(ConnectorModel)
        query = query.where(
            sql(sql_query).bindparams(
                product=self.product.id,
                date_digital_published=self.date_digital_published,
            )
        )
        try:
            return next(self.repository.search(query))
        except StopIteration:
            return None

    @staticmethod
    def published_days_ago(days_ago):
        query = """
        type=:volume
        AND published = true
        AND volume_date_digital_published >= :start_time
        AND volume_date_digital_published <= :end_time
        ORDER BY date_last_published DESC
        """

        start_time = pendulum.now().subtract(days=(days_ago + 1)).to_date_string()
        end_time = pendulum.now().subtract(days=days_ago).to_date_string()
        query = select(ConnectorModel).where(
            sql(query).bindparams(
                volume=VolumeType.type,
                start_time=start_time,
                end_time=end_time,
            )
        )

        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        try:
            return next(repository.search(query))
        except StopIteration:
            return None

    def get_cover(self, cover_id, product_id=None, use_fallback=True):
        if product_id is None and use_fallback:
            product_id = self.product.id
        if product_id and product_id not in [prod.id for prod in self._all_products]:
            err = ValueError(f'{product_id} is not a valid product id for {self}')
            current_span = opentelemetry.trace.get_current_span()
            current_span.record_exception(err)
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
                'Cover id {} or product id {} are not valid.'.format(cover_id, product_id)
            )
        path = '//covers/cover[@id="{}" and @product_id="{}"]'.format(cover_id, product_id)
        node = self.xml.xpath(path)
        if node:
            self.xml.find('covers').remove(node[0])
        if imagegroup is not None:
            node = lxml.builder.E.cover(
                id=cover_id, product_id=product_id, href=imagegroup.uniqueId
            )
            self.xml.find('covers').append(node)
        super().__setattr__('_p_changed', True)

    def get_cover_title(self, product_id):
        path = f'//volume/title-overrides/title[@product_id="{product_id}"]'
        node = self.xml.xpath(path)
        return node[0].text if node else None

    def set_cover_title(self, product_id, title):
        title_overrides_path = '//volume/title-overrides'
        if not self.xml.xpath(title_overrides_path):
            self.xml.append(lxml.builder.E('title-overrides'))
        path = f'//volume/title-overrides/title[@product_id="{product_id}"]'
        node = self.xml.xpath(path)
        if node:
            self.xml.find('title-overrides').remove(node[0])
        if title is not None:
            node = lxml.builder.E.title(title, product_id=product_id)
            self.xml.find('title-overrides').append(node)
        super().__setattr__('_p_changed', True)

    def _is_valid_cover_id_and_product_id(self, cover_id, product_id):
        cover_ids = list(zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(self))
        product_ids = [prod.id for prod in self._all_products]
        return cover_id in cover_ids and product_id in product_ids

    def _query_content_for_current_volume(self):
        query = """
        volume_year = :year
        AND volume_number = :volume
        AND product IN :products
        """
        bind_params = [bindparam('products', [x.id for x in self._all_products], expanding=True)]
        return select(ConnectorModel).where(
            sql(query).bindparams(*bind_params, year=self.year, volume=self.volume)
        )

    def change_contents_access(
        self,
        access_from,
        access_to,
        published=True,
        exclude_performing_articles=True,
    ):
        conditions = """
        access = :access_from
        AND NOT channels @> '[["zeit-magazin", "wochenmarkt"]]'
        AND name <> 'ausgabe'
        """
        query = self._query_content_for_current_volume().where(
            sql(conditions).bindparams(access_from=access_from)
        )
        if published:
            query = query.where(sql('published = true'))

        if exclude_performing_articles:
            try:
                content_to_filter = _find_performing_articles_via_webtrekk(self)
                if content_to_filter:
                    query = query.where(
                        sql('(parent_path, name) NOT IN :content').bindparams(
                            bindparam('content', content_to_filter, expanding=True)
                        )
                    )
            except Exception as err:
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(err)

        contents = []
        for content in self.repository.search(query):
            contents.append(content)
            try:
                with zeit.cms.checkout.helper.checked_out(content) as co:
                    co.access = access_to
                    zope.lifecycleevent.modified(
                        co,
                        zope.lifecycleevent.Attributes(
                            zeit.cms.content.interfaces.ICommonMetadata, 'access'
                        ),
                    )
            except Exception as err:
                current_span = opentelemetry.trace.get_current_span()
                current_span.record_exception(err)
        return contents

    def articles_with_references_for_publishing(self):
        conditions = """
        type='article'
        AND published=false
        AND unsorted @@ '$.workflow.urgent == "yes"'
        """
        query = self._query_content_for_current_volume().where(sql(conditions))

        publishable_content = set()
        for article in self.repository.search(query):
            publishable_content.update(self._with_publishable_references(article))

        publishable_content.add(self)
        return list(publishable_content)

    def _with_publishable_references(self, article):
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

    def get_audios(self):
        feed_url = 'https://medien.zeit.de/feeds/die-zeit/issue'
        response = requests.get(
            feed_url,
            params={'year': self.year, 'number': self.volume},
            timeout=2,
        )
        data = response.json()
        result = {}
        for part_of_volume in data['dataFeedElement'][0]['item']['hasPart']:
            for article in part_of_volume.get('hasPart', []):
                mediasync_id = article.get('identifier', None)
                mp3_object = next(
                    filter(
                        lambda x: x.get('encodingFormat') == 'audio/mpeg',
                        article.get('associatedMedia', []),
                    ),
                    None,
                )
                if mediasync_id and mp3_object:
                    result[mediasync_id] = {
                        'url': mp3_object.get('url', None),
                        'duration': mp3_object.get('duration', None),
                    }
        return result


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
    config = zeit.cms.config.package('zeit.content.volume')
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
            (parent_path, sep, name) = f'/{url}'.rpartition('/')
            urls.add((parent_path, name))
    return list(urls)


@zeit.cms.cli.runner(
    principal=zeit.cms.cli.from_config('zeit.content.volume', 'access-control-principal')
)
def change_access():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days-ago', type=int, help='Select volume that was published x days ago.')
    parser.add_argument('--uniqueid', help='Select volume by uniqueId.')
    options = parser.parse_args()

    if bool(options.days_ago) == bool(options.uniqueid):
        parser.error('You have to specify either uniqueid or days-ago')

    volume = None
    try:
        if options.uniqueid:
            volume = zeit.cms.interfaces.ICMSContent(options.uniqueid)
        else:
            volume = Volume.published_days_ago(options.days_ago)
    except Exception as err:
        current_span = opentelemetry.trace.get_current_span()
        current_span.record_exception(err)
    if not volume:
        return
    content = volume.change_contents_access('abo', 'registration')
    content.extend(volume.change_contents_access('dynamic', 'registration'))
    for item in content:
        IPublish(item).publish(background=False)
