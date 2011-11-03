# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.interface.common.mapping
import zope.schema.interfaces
import zope.schema


class ITagger(zope.interface.Interface):
    """Interface to whatever prduces tags for a content object."""

    def __call__():
        """Update tags of context.

        Usually this means to send the text to a tagging service which returns
        the relevant tagging data.

        """


class ITag(zope.interface.Interface):
    """A tag."""

    code = zope.schema.TextLine(
        title=u'Internal tag id')

    label = zope.schema.TextLine(
        title=u'User visible text of tag')


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


class ITaggable(zope.interface.Interface):

    keywords = zope.schema.Tuple(
        title=_("Keywords"),
        required=False,
        default=(),
        value_type=zope.schema.Choice(source=TagSource))

    disabled_keywords = zope.schema.Tuple(
        title=_("Disabled keywords"),
        required=False,
        default=(),
        readonly=True,
        value_type=zope.schema.Choice(source=TagSource))


ID_NAMESPACE = 'tag://'
