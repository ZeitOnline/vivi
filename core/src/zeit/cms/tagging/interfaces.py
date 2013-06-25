# Copyright (c) 2011-2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zeit.cms.content.sources
import zope.interface
import zope.interface.common.mapping
import zope.schema.interfaces


class IReadTagger(zope.interface.common.mapping.IEnumerableMapping):
    """Tagger."""


class IWriteTagger(zope.interface.Interface):

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


class ITagsForContent(zope.schema.interfaces.IIterableSource):
    pass


class TagsForContent(zc.sourcefactory.contextual.BasicContextualSourceFactory):

    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        zope.interface.implements(ITagsForContent)

    def getValues(self, context):
        tagger = ITagger(context, None)
        if tagger is None:
            return []
        return (tagger[code] for code in tagger)

    def getTitle(self, context, value):
        return value.label

    def getToken(self, context, value):
        return value.code


class IReadWhitelist(zope.interface.common.mapping.IEnumerableMapping):

    def search(term):
        """Returns a list of tags whose labels contain the given term."""


class IWhitelist(IReadWhitelist, zope.interface.common.mapping.IWriteMapping):
    """Tag whitelist

    The whitelist contains all selectable tags.

    """


class IWhitelistSource(zope.schema.interfaces.IIterableSource):
    """Tag whitelist"""


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
