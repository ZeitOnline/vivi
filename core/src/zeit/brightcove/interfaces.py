# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zope.interface
import zope.schema


class IAPIConnection(zope.interface.Interface):
    """Brightcove API connection."""


class IRepository(zope.interface.Interface):
    """A repostory for accessing brightcove videso.


    Content from brightcove has unique ids in the form::

        brighcove:<type>:<id>.

    """

    def __getitem__(key):
        """Return IBrightcoveContent for given key.

        Key was the form: ``<type>:<id>``

        """



class IBrightcoveContent(zope.interface.Interface):

    supertitle = zope.schema.TextLine(
        title=_("Kicker"),
        description=_("Please take care of capitalisation."),
        max_length=1024,
        required=False)

    title = supertitle = zope.schema.TextLine(
        title=_("Title"))

    teaserText = zope.schema.Text(
        title=_("Teaser text"),
        required=False,
        max_length=170)

    subtitle = zope.schema.Text(
        title=_("Video subtitle"),
        required=False,
        max_length=5000)

    ressort = zope.schema.Choice(
        title=_("Ressort"),
        source=zeit.cms.content.sources.NavigationSource())

    serie = zope.schema.Choice(
        title=_("Serie"),
        source=zeit.cms.content.sources.SerieSource(),
        required=False)

    product_id = zope.schema.Choice(
        title=_('Product id'),
        default='ZEDE',
        source=zeit.cms.content.sources.ProductSource())

    keywords = zope.schema.Tuple(
        title=_("Keywords"),
        required=False,
        default=(),
        unique=True,
        value_type=zope.schema.Object(
            zeit.cms.content.interfaces.IKeyword))

    dailyNewsletter = zope.schema.Bool(
        title=_("Daily newsletter"),
        description=_(
            "Should this article be listed in the daily newsletter?"),
        default=False)

    banner = zope.schema.Bool(
        title=_("Banner"),
        default=False)

    banner_id = zope.schema.TextLine(
        title=_('Banner id'),
        required=False)

    breaking_news = zope.schema.Bool(
        title=_('Breaking news'),
        default=False)


class IVideo(IBrightcoveContent):
    """A video."""
