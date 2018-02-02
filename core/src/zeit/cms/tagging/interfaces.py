from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.tagging.source
import zope.interface
import zope.interface.common.mapping
import zope.schema
import zope.schema.interfaces


class IReadTagger(zope.interface.common.mapping.IEnumerableMapping):
    """Tagger."""

    pinned = zope.interface.Attribute('list of tag codes that are pinned.')

    def to_xml():
        pass


class IWriteTagger(zope.interface.common.mapping.IWriteMapping):

    def update():
        """Update tags of context.

        Ususally this means to send the text to a tagging service which returns
        the relevant tagging data.

        """

    def set_pinned(codes):
        """Mark the tags with the given codes as pinned.
        """


class ITagger(IReadTagger, IWriteTagger):
    """Tagger.

    The tagger allows to iterate over tags and to remove and add tags.

    """


class ITag(zeit.cms.interfaces.ICMSContent):
    """A tag."""

    code = zope.schema.TextLine(
        title=u'Internal tag id')

    label = zope.schema.TextLine(
        title=u'User visible text of tag')

    pinned = zope.schema.Bool(
        title=u'Prevent this tag from being changed by automatic processes?')

    entity_type = zope.schema.TextLine(
        title=u'Entity type (e.g. Person, Location), may be None.')

    url_value = zope.schema.ASCIILine(
        title=u'Label encoded/normalized for use in an URL.')


class IWhitelist(zope.interface.Interface):
    """The whitelist contains all selectable tags providing `ITag`."""

    def search(term):
        """Return a list of tags whose labels contain the given term."""

    def locations(term):
        """Return a list of location tags whose labels contain given term."""

    def get(id):
        """Return the tag for the given id."""


ID_NAMESPACE = 'tag://'


class KeywordConfigurationHelper(zeit.cms.content.sources.SimpleXMLSource):

    config_url = 'keyword-configuration'

    def getValues(self):
        tree = self._get_tree()
        return [int(tree.xpath('/keywords/article/display_num')[0].text)]

_KEYWORD_CONFIG_HELPER = KeywordConfigurationHelper()


class KeywordConfiguration(object):

    @property
    def keywords_shown(self):
        return list(_KEYWORD_CONFIG_HELPER)[0]

KEYWORD_CONFIGURATION = KeywordConfiguration()


class TooFewKeywords(zope.schema.interfaces.TooShort):
    __doc__ = _('Too few keywords given.')


class Keywords(zope.schema.Tuple):

    def __init__(self, **kw):
        kw.setdefault('title', _('Keywords'))
        kw.setdefault('value_type', zope.schema.Choice(
            source=zeit.cms.tagging.source.WhitelistSource()))
        super(Keywords, self).__init__(**kw)

    def _validate(self, value):
        try:
            super(Keywords, self)._validate(value)
        except zope.schema.interfaces.TooShort:
            raise TooFewKeywords()


class ITopicpages(zope.interface.Interface):
    """Utility to retrieve (paginated) information about topic pages."""

    def get_topics(start=0, rows=25):
        """Returns an IResult containing dicts with keys ``id`` and ``title``.

        Our topic pages typically have URLs like www.zeit.de/thema/<id>.
        """
