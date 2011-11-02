# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
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


class IAppliedTag(zope.interface.Interface):
    """A generic tag on an object."""

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


class TagSource(zope.schema.interfaces.IIterableSource):
    """Source of possible tags for a content object.

    This is a ContextSourceBinder that chooses a concrete TagSource according
    to the content type.
    """

zope.interface.alsoProvides(
    TagSource, zope.schema.interfaces.IContextSourceBinder)


class IAutomaticTagSource(TagSource):
    """TagSource that classifies (i.e. assigns tags to) a content object,
    and yields those as possible tags for that object.

    This means that the user can only deselect tags, but not any of his own.
    """

    def update():
        """Update the list of tags from the backend."""


class IWhitelistTagSource(TagSource):
    """TagSource that is populated by IWhitelist, independent of a content
    object.

    This means that the user can choose which tags of these to apply to the
    content object.
    """


class IReadWhitelist(zope.interface.common.mapping.IEnumerableMapping):

    def search(prefix):
        """Returns a list of tags whose lables start with the given prefix."""


class IWhitelist(IReadWhitelist, zope.interface.common.mapping.IWriteMapping):
    """Tag whitelist

    The whitelist contains all selectable tags.

    """


ID_NAMESPACE = 'tag://'
