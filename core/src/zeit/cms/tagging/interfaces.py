# Copyright (c) 2011-2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.tagging.source import IWhitelistSource
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zeit.cms.content.sources
import zeit.cms.tagging.source
import zope.interface
import zope.interface.common.mapping
import zope.schema
import zope.schema.interfaces


class IReadTagger(zope.interface.common.mapping.IEnumerableMapping):
    """Tagger."""


class IWriteTagger(zope.interface.common.mapping.IWriteMapping):

    def update():
        """Update tags of context.

        Ususally this means to send the text to a tagging service which returns
        the relevant tagging data.

        """


class ITagger(IReadTagger, IWriteTagger):
    """Tagger.

    The tagger allows to iterate over tags and to remove and add tags.

    """


class ITag(zope.interface.Interface):
    """A tag."""

    code = zope.schema.TextLine(
        title=u'Internal tag id')

    label = zope.schema.TextLine(
        title=u'User visible text of tag')


class IReadWhitelist(zope.interface.common.mapping.IEnumerableMapping):

    def search(term):
        """Returns a list of tags whose labels contain the given term."""


class IWhitelist(IReadWhitelist, zope.interface.common.mapping.IWriteMapping):
    """Tag whitelist

    The whitelist contains all selectable tags.

    """


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
