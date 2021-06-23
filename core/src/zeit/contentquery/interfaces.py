from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import CONFIG_CACHE
import collections
import json
import logging
import re
import six
import zc.sourcefactory.basic
import zeit.cms.content.property
import zeit.cms.content.sources
import zeit.content.article.interfaces
import zeit.content.cp.field
import zeit.content.cp.source
import zope.interface

log = logging.getLogger(__name__)


class AutomaticFeed(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, url, timeout):
        super(AutomaticFeed, self).__init__(id, title, None)
        self.url = url
        self.timeout = timeout


class AutomaticFeedSource(zeit.cms.content.sources.ObjectSource,
                          zeit.cms.content.sources.SimpleContextualXMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-automatic-feed-source'
    default_filename = 'cp-automatic-feeds.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        for node in self._get_tree().iterchildren('*'):
            feed = AutomaticFeed(
                six.text_type(node.get('id')),
                six.text_type(node.text.strip()),
                six.text_type(node.get('url')),
                int(node.get('timeout', 2))
            )
            result[feed.id] = feed
        return result


AUTOMATIC_FEED_SOURCE = AutomaticFeedSource()


class QuerySortOrderSource(zeit.cms.content.sources.SimpleDictSource):

    values = collections.OrderedDict((
        ('payload.workflow.date_last_published_semantic:desc',
         _('query-sort-order-last-published-semantic')),
        ('payload.document.last-semantic-change:desc',
         _('query-sort-order-last-semantic-change')),
        ('payload.document.date_first_released:desc',
         _('query-sort-order-first-released')),
    ))


class QueryTypeSource(zeit.cms.content.sources.SimpleDictSource):

    values = collections.OrderedDict([
        ('channels', _('query-type-channels')),
        ('serie', _('query-type-serie')),
        ('product', _('query-type-product')),
        ('ressort', _('query-type-ressort')),
        ('genre', _('query-type-genre')),
        ('authorships', _('query-type-authorships')),
        ('access', _('query-type-access')),
        ('content_type', _('query-type-content-type')),
    ])


class QueryOperatorSource(zeit.cms.content.sources.SimpleDictSource):

    values = collections.OrderedDict([
        ('eq', _('query-operator-equal')),
        ('neq', _('query-operator-notequal')),
    ])


class TopicpageFilterSource(zc.sourcefactory.basic.BasicSourceFactory,
                            zeit.cms.content.sources.CachedXMLBase):

    COMMENT = re.compile(r'\s*//')

    product_configuration = 'zeit.content.cp'
    config_url = 'topicpage-filter-source'
    default_filename = 'topicpage-filters.json'

    def json_data(self):
        result = collections.OrderedDict()
        for row in self._get_tree():
            if len(row) != 1:
                continue
            key = list(row.keys())[0]
            result[key] = row[key]
        return result

    @CONFIG_CACHE.cache_on_arguments()
    def _get_tree_from_url(self, url):
        try:
            data = []
            for line in six.moves.urllib.request.urlopen(url):
                line = six.ensure_text(line)
                if self.COMMENT.search(line):
                    continue
                data.append(line)
            data = '\n'.join(data)
            return json.loads(data)
        except Exception:
            log.warning(
                'TopicpageFilterSource could not parse %s', url, exc_info=True)
            return {}

    def getValues(self):
        return self.json_data().keys()

    def getTitle(self, value):
        return self.json_data()[value].get('title', value)

    def getToken(self, value):
        return value


class TopicpageOrderSource(zeit.cms.content.sources.SimpleDictSource):

    values = collections.OrderedDict([
        ('date', _('tms-order-date')),
        ('relevance', _('tms-order-relevance')),
        ('kpi_visits', _('tms-order-kpi_visits')),
        ('kpi_comments', _('tms-order-kpi_comments')),
        ('kpi_subscriptions', _('tms-order-kpi_subscriptions')),
    ])


class QuerySubRessortSource(zeit.cms.content.sources.SubRessortSource):

    def _get_parent_value(self, context):
        # `context` is the IArea, which is adaptable to `parent_value_iface`
        # ICommonMetadata, since it is adaptable to ICenterPage -- but of
        # course we don't want to restrict the query subressort according to
        # the CP's ressort. So we disable this validation here and rely on the
        # fact that the widget will only offer matching subressorts anyway.
        return None


class IQueryConditions(zeit.content.article.interfaces.IArticle):

    # ICommonMetadata uses a ReferenceField, which makes no sense for `query`.
    authorships = zope.schema.Choice(
        title=_("Authors"),
        source=zeit.cms.content.interfaces.authorSource,
        required=False)

    # ICommonMetadata has ressort and sub_ressort in separate fields, but we
    # need them combined. And so that whitespace-separated serializing works,
    # we wrap it in a tuple to reuse the DAVPropertyConverter for `channels`.
    ressort = zope.schema.Tuple(value_type=zc.form.field.Combination(
        (zope.schema.Choice(
            title=_('Ressort'),
            source=zeit.cms.content.sources.RessortSource()),
         zope.schema.Choice(
             title=_('Sub ressort'),
             source=QuerySubRessortSource(),
             required=False)),
        default=(),
        required=False))
    zope.interface.alsoProvides(
        ressort.value_type, zeit.cms.content.interfaces.IChannelField)

    # non-ICommonMetadata field
    content_type = zope.schema.Choice(
        title=_("Content type"),
        source=zeit.cms.content.sources.CMSContentTypeSource())


class IContentQuery(zope.interface.Interface):
    """Mechanism to retrieve content objects.
    Used to register named adapters for the different IArea.automatic_type's
    and article module ITopicbox.automatic_type's
    """

    total_hits = zope.interface.Attribute(
        'Total number of available results (only available after calling)')

    def __call__(self):
        """Returns list of content objects."""


class IConfiguration(zope.interface.Interface):

    automatic_type = zope.interface.Attribute("Automatic type")
    automatic_type.__doc__ = """
        Determines from where content objects will be retrieved.
        Will look up a utility of that name for IContentQuery."""

    count = zope.schema.Int(title=_('Amount of teasers'), default=15)

    existing_teasers = zope.interface.Attribute(
        """Returns a set of ICMSContent objects that are already present on
        the CP. If IArea.hide_dupes is True, these should be not be repeated,
        and thus excluded from our query result.""")

    hide_dupes = zope.schema.Bool(
        title=_('Hide duplicate teasers'),
        default=True)

    query = zope.schema.Tuple(
        title=_('Custom Query'),
        value_type=zeit.content.cp.field.DynamicCombination(
            zope.schema.Choice(
                title=_('Custom Query Type'),
                source=QueryTypeSource(), default='channels'),
            IQueryConditions,
            zope.schema.Choice(
                title=_('Custom Query Operator'),
                source=QueryOperatorSource(), default='eq'),
        ),
        default=(),
        required=False)

    query_order = zope.schema.Choice(
        title=_('Sort order'),
        source=QuerySortOrderSource(),
        default=u'payload.workflow.date_last_published_semantic:desc',
        required=True)

    elasticsearch_raw_query = zope.schema.Text(
        title=_('Elasticsearch raw query'),
        required=False)

    elasticsearch_raw_order = zope.schema.TextLine(
        title=_('Sort order'),
        default=u'payload.document.date_first_released:desc',
        required=False)

    is_complete_query = zope.schema.Bool(
        title=_('Take over complete query body'),
        description=_('Remember to add payload.workflow.published:true'),
        default=False,
        required=False)

    referenced_cp = zope.schema.Choice(
        title=_('Get teasers from CenterPage'),
        source=zeit.content.cp.source.centerPageSource,
        required=False)

    referenced_topicpage = zope.schema.TextLine(
        title=_('Referenced Topicpage'),
        required=False)

    topicpage_filter = zope.schema.Choice(
        title=_('Topicpage filter'),
        source=TopicpageFilterSource(),
        required=False)

    topicpage_order = zope.schema.Choice(
        title=_('Topicpage order'),
        source=TopicpageOrderSource(),
        default='date'
    )

    related_topicpage = zope.schema.TextLine(
        title=_('Referenced Topicpage Id'),
        required=False)

    rss_feed = zope.schema.Choice(
        title=_('RSS-Feed'),
        source=AUTOMATIC_FEED_SOURCE,
        required=False)
