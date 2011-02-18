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
    """A generic tag on an object."""

    code  = zope.schema.TextLine(
        title=u'Internal tag id')

    label = zope.schema.TextLine(
        title=u'User visible text of tag')

    type = zope.schema.TextLine(
        title=u"Tag type (person, topic, keyword, ...)")

    disabled = zope.schema.Bool(
        title=u'Disabled')

    weight = zope.schema.Int(
        title=_('Weight'),
        description=_(
            'The higher the weight the more important is a tag. Ideally no '
            'two tags have the same weight, but that is not enforced.'),
        required=False,
        default=0)


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


class IWhitelist(zope.schema.interfaces.IIterableSource):
    """Tag whitelist

    The whitelist contains all selectable tags.

    """


class Whitelist(zc.sourcefactory.basic.BasicSourceFactory):

    class source_class(zc.sourcefactory.source.FactoredSource):
        zope.interface.implements(IWhitelist)

    def getValues(self):
        # XXX currently there are no tags, see #8624
        return []
