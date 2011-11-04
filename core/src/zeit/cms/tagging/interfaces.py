# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zc.sourcefactory.source
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

    def search(prefix):
        """Returns a list of tags whose lables start with the given prefix."""


class IWhitelist(IReadWhitelist, zope.interface.common.mapping.IWriteMapping):
    """Tag whitelist

    The whitelist contains all selectable tags.

    """


class IWhitelistSource(zope.schema.interfaces.IIterableSource):
    """Tag whitelist"""


ID_NAMESPACE = 'tag://'
