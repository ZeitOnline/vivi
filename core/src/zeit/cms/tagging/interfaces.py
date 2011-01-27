# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.contextual
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


class TagsForContent(zc.sourcefactory.contextual.BasicContextualSourceFactory):

    def getValues(self, context):
        tagger = ITagger(context)
        return (tagger[code] for code in tagger)

    def getTitle(self, context, value):
        return value.label
