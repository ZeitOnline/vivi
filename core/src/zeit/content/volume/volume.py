import itertools
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.cp.interfaces
import zeit.content.volume.interfaces
import zeit.content.portraitbox.interfaces
import zeit.content.infobox.interfaces
import zeit.edit.interfaces
import zeit.solr.query
import zeit.workflow.interfaces
import zope.interface
import zope.lifecycleevent
import zope.schema
import logging


log = logging.getLogger()


class Volume(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.IAsset)

    default_template = u"""\
        <volume xmlns:py="http://codespeak.net/lxml/objectify/pytype">
            <head/>
            <body/>
            <covers/>
        </volume>
    """

    zeit.cms.content.dav.mapProperties(
        zeit.content.volume.interfaces.IVolume,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('date_digital_published', 'year', 'volume'))

    _product_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        zeit.workflow.interfaces.WORKFLOW_NS,
        'product-id')

    assets_to_publish = [zeit.content.portraitbox.interfaces.IPortraitbox,
                         zeit.content.infobox.interfaces.IInfobox
                         ]

    @property
    def product(self):
        source = zeit.content.volume.interfaces.IVolume['product'].source(self)
        for value in source:
            if value.id == self._product_id:
                return value

    @product.setter
    def product(self, value):
        if self._product_id == value.id:
            return
        self._product_id = value.id if value is not None else None

    _teaserText = zeit.cms.content.dav.DAVProperty(
        zeit.content.volume.interfaces.IVolume['teaserText'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'teaserText')

    @property
    def teaserText(self):
        text = self._teaserText
        if text is None:
            config = zope.app.appsetup.product.getProductConfiguration(
                'zeit.content.volume')
            text = config['default-teaser-text'].decode('utf-8')
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
        return text.format(
            year=context.year,
            name=str(context.volume).rjust(2, '0'))

    @property
    def previous(self):
        return self._find_in_order(None, self.date_digital_published, 'desc')

    @property
    def next(self):
        return self._find_in_order(self.date_digital_published, None, 'asc')

    @property
    def _all_products(self):
        return [self.product] + self.product.dependent_products

    def _find_in_order(self, start, end, sort):
        if len(filter(None, [start, end])) != 1:
            return None
        # Inspired by zeit.web.core.view.Content.lineage.
        Q = zeit.solr.query
        query = Q.and_(
            Q.field_raw('type', VolumeType.type),
            Q.field('product_id', self.product.id),
            Q.datetime_range('date_digital_published', start, end),
            Q.not_(Q.field('uniqueId', self.uniqueId))
        )
        solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        result = solr.search(query, sort='date_digital_published ' + sort,
                             fl='uniqueId', rows=1)
        if not result:
            return None
        # Since `sort` is passed in accordingly, and we exclude ourselves,
        # the first result (if any) is always the one we want.
        return zeit.cms.interfaces.ICMSContent(
            iter(result).next()['uniqueId'], None)

    def get_cover(self, cover_id, product_id=None, use_fallback=True):
        if product_id is None and use_fallback:
            product_id = self.product.id
        if product_id and product_id not in \
                [prod.id for prod in self._all_products]:
            log.warning('%s is not a valid product id for %s' % (
                product_id, self))
            return None
        path = '//covers/cover[@id="{}" and @product_id="{}"]' \
            .format(cover_id, product_id)
        node = self.xml.xpath(path)
        uniqueId = node[0].get('href') if node else None
        if uniqueId:
            return zeit.cms.interfaces.ICMSContent(uniqueId, None)
        if use_fallback:
            # Fall back to the main product (which must be self.product,
            # since we respond only to ids out of self._all_products)
            # Recursive call of this function with the main product ID
            return self.get_cover(
                cover_id, self.product.id, use_fallback=False)

    def set_cover(self, cover_id, product_id, imagegroup):
        if not self._is_valid_cover_id_and_product_id(cover_id, product_id):
            raise ValueError("Cover id {} or product id {} are not "
                             "valid.".format(cover_id, product_id))
        path = '//covers/cover[@id="{}" and @product_id="{}"]' \
            .format(cover_id, product_id)
        node = self.xml.xpath(path)
        if node:
            self.xml.covers.remove(node[0])
        if imagegroup is not None:
            node = lxml.objectify.E.cover(id=cover_id,
                                          product_id=product_id,
                                          href=imagegroup.uniqueId)
            lxml.objectify.deannotate(node[0], cleanup_namespaces=True)
            self.xml.covers.append(node)
        super(Volume, self).__setattr__('_p_changed', True)

    def _is_valid_cover_id_and_product_id(self, cover_id, product_id):
        cover_ids = list(zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(
            self))
        product_ids = [prod.id for prod in self._all_products]
        return cover_id in cover_ids and product_id in product_ids

    def all_content_via_solr(self, additional_query_contstraints=None):
        """
        Get all content for this volume via Solr.
        If u pass a list of additional query strings, they will be added as
        an AND-operand to the query field.
        """
        if not additional_query_contstraints:
            additional_query_contstraints = []
        Q = zeit.solr.query
        solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        query = Q.and_(
            Q.not_(Q.field('uniqueId', self.uniqueId)),
            Q.or_(*[Q.field('product_id', p.id) for p in
                    self._all_products]),
            Q.field_raw('year', self.year),
            Q.field_raw('volume', self.volume),
            *additional_query_contstraints
        )
        result = solr.search(query, fl='uniqueId', rows=1000)
        # We assume a maximum content amount per usual production print volume
        assert result.hits < 250
        content = []
        for item in result:
            item = zeit.cms.interfaces.ICMSContent(item['uniqueId'], None)
            if item is not None:
                content.append(item)
        return content

    def change_contents_access(self, access_from, access_to, published=True):
        Q = zeit.solr.query
        constraints = [Q.field('access', access_from)]
        if published:
            constraints.append(Q.field_raw('published', 'published*'))
        cnts = self.all_content_via_solr(constraints)
        for cnt in cnts:
            try:
                with zeit.cms.checkout.helper.checked_out(cnt) as co:
                    co.access = unicode(access_to)
                    zope.lifecycleevent.modified(
                        co, zope.lifecycleevent.Attributes(
                            zeit.cms.content.interfaces.ICommonMetadata,
                            'access')
                    )
            except:
                log.error("Couldn't change access for {}. Skipping "
                          "it.".format(cnt.uniqueId))
        return cnts

    def content_with_references_for_publishing(self):
        Q = zeit.solr.query
        additional_constraints = [
            Q.field('published', 'not-published'),
            Q.and_(
                Q.bool_field('urgent', True),
                Q.field_raw(
                    'type',
                    zeit.content.article.article.ArticleType.type)),
        ]
        articles_to_publish = self.all_content_via_solr(
            additional_query_contstraints=additional_constraints)
        # Flatten the list of lists and remove duplicates
        return list(set(itertools.chain.from_iterable(
            [self._with_references(article) for article in
             articles_to_publish])))

    def _with_references(self, article):
        """
        :param content: CMSContent
        :return: [referenced_content1, ..., content]
        """
        # XXX Using zeit.cms.relation.IReferences would make sense here as
        # well but due to some license issues with images referenced by
        # articles we have to be careful what we want to publish
        with_dependencies = [
            content for content in zeit.edit.interfaces.IElementReferences(
                article, []) if self._needs_publishing(content)
        ]
        with_dependencies.append(article)
        return with_dependencies

    def _needs_publishing(self, content):
        # Dont publish content which is already published
        if zeit.cms.workflow.interfaces.IPublishInfo(content).published:
            return False
        # content has to provide one of interfaces defined above
        return any([interface.providedBy(content) for interface
                    in self.assets_to_publish])


class VolumeType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Volume
    interface = zeit.content.volume.interfaces.IVolume
    title = _('Volume')
    type = 'volume'


class VolumeMetadata(grok.Adapter):
    """Since ICenterPage inherits from ICommonMetadata, we need to ensure
    that adapting a volume to ICommonMetadata returns fields from the volume,
    and not the CP.
    """

    grok.context(zeit.content.volume.interfaces.IVolume)
    grok.implements(zeit.cms.content.interfaces.ICommonMetadata)

    missing = object()

    def __getattr__(self, name):
        value = getattr(self.context, name, self.missing)
        if value is self.missing:
            field = zeit.cms.content.interfaces.ICommonMetadata.get(name, None)
            return field.default
        return value


class CoverDependency(grok.Adapter):
    """
    If a Volume is published, its covers are published as well.
    """
    grok.context(zeit.content.volume.interfaces.IVolume)
    grok.implements(zeit.workflow.interfaces.IPublicationDependencies)

    def get_dependencies(self):
        cover_names = zeit.content.volume.interfaces.VOLUME_COVER_SOURCE(
            self.context)
        covers = []
        for product in self.context._all_products:
            for cover_name in cover_names:
                cover = self.context.get_cover(cover_name,
                                               product_id=product.id,
                                               use_fallback=False)
                if cover:
                    covers.append(cover)
        return covers


@grok.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@grok.implementer(zeit.content.volume.interfaces.IVolume)
def retrieve_volume_using_info_from_metadata(context):
    if (context.year is None or context.volume is None or
            context.product is None):
        return None

    unique_id = None
    if context.product.volume and context.product.location:
        unique_id = Volume._fill_template(context, context.product.location)
    else:
        main_product = zeit.content.volume.interfaces.PRODUCT_SOURCE(
            context).find(context.product.relates_to)
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
        main_product = zeit.content.volume.interfaces.PRODUCT_SOURCE(
            context).find(context.product.relates_to)
        if main_product and main_product.centerpage:
            unique_id = context.fill_template(main_product.centerpage)
    cp = zeit.cms.interfaces.ICMSContent(unique_id, None)
    if not zeit.content.cp.interfaces.ICenterPage.providedBy(cp):
        return None
    return cp
