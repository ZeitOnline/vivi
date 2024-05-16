import json
import logging

import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.content.text.interfaces
import zeit.content.text.jinja


log = logging.getLogger(__name__)


class IMessage(zope.interface.Interface):
    get_text_from = zope.interface.Attribute(
        'Fieldname from `IPushMessages` to read the text for the notification'
    )

    text = zope.interface.Attribute(
        'Property that can be overriden if `get_text_from` is not sufficient '
        'to retrieve the text for the notification'
    )

    def send():
        """Send push notification to external service via `IPushNotifier`.

        Will fetch the `IPushNotifier` utility using the name that was used to
        register this `IMessage` adapter. Calls `IPushNotifier.send()`
        to perform the actual sending.
        """


class IPushNotifier(zope.interface.Interface):
    def send(text, link, **kw):
        """Sends given ``text`` as a push message through an external service.

        The ``link`` (an URL) will be integrated into the message (how this
        happens depends on the medium, possibilities include appending to the
        text, attaching as metadata, etc.).

        Additional kw parameters:

        * ``type``: Name of the external service.

        * ``message``: The IMessage object
        [only used in `mobile`]

        * ``enabled``: If the service is enabled.

        * ``override_text``: Text that should be used instead of the given
          `text` parameter. [only `mobile` & `facebook`]

        * ``account``: Send push notification using given account.
          [only `facebook`]

        """


class WebServiceError(Exception):
    """Web service was unable to process a request due to semantic problems.

    For example, a response with HTTP status code "401 Unauthorized" should
    raise this error.

    """


class TechnicalError(Exception):
    """Web service was unable to process a request due to technical errors.

    For example, a response with HTTP status code "500 Server Error" should
    raise this error.

    """


class IPushMessages(zope.interface.Interface):
    """Configures push services that are notified if context is published.

    Available services are stored in `message_config` on checkin of context.
    When the context is published, send a push notification for each stored
    service whose configuration defines it as `enabled` by looking up a named
    `IMessage` adapter that forwards the actual push to an `IPushNotifier`
    utility.

    """

    short_text = zope.schema.Text(
        title=_('Short push text'),
        required=False,
        # 256 + 1 Space + 23 characters t.co-URL = 140
        #
        # XXX It's not yet clear what we can do when the user enters another
        # URL as part of the tweet and that URL gets *longer* during the
        # shortening process.
        max_length=256,
    )

    """A message configuration is a dict with at least the following keys:
       - type: Kind of service (twitter, facebook, ...). Must correspond
         to the utility name of an IPushNotifier.
       - enabled: Boolean. This allows keeping the message configuration even
         when it should not be used at the moment, e.g. for different text to
         different accounts.

    Any other keys are type-dependent. (A common additional key is ``account``,
    e.g. Twitter and Facebook support posting to different accounts.)

    """
    message_config = zope.schema.Tuple(required=False, default=())

    messages = zope.interface.Attribute(
        'List of IMessage objects, one for each enabled message_config entry'
    )

    def get(**query):
        """Returns the first entry in message_config that matches the given
        query key/values.
        """

    def set(query, **values):
        """Updates the first entry in message_config that matches the given
        query key/values with the given values. If none is found, a new entry
        is appended, combining query and values.
        """

    def delete(query):
        """Removes the first entry in message_config that matches the given
        query key/values."""


class IPushURL(zope.interface.Interface):
    """Interface to adapt `ICMSContent` to the base URL for push notifications.

    Usually the result is the `uniqueId` of the `ICMSContent`, but this
    interface serves as an extension point for special treatments of certain
    content types, e.g. `zeit.content.link` objects.

    """


class ISocialConfig(zope.interface.Interface):
    """Configuration for social media services."""


class IBanner(zope.interface.Interface):
    """
    Utility to manage the homepage banner.
    """

    article_id = zope.interface.Attribute('UniqueId of the current article in the homepage banner')


class ITwitterCredentials(zope.interface.Interface):
    """BBB"""


class MobileButtonsSource(zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.push'
    config_url = 'mobile-buttons'
    default_filename = 'push-mobile-buttons.xml'
    attribute = 'id'


MOBILE_BUTTONS_SOURCE = MobileButtonsSource()


class PayloadTemplateSource(zeit.cms.content.sources.FolderItemSource):
    product_configuration = 'zeit.push'
    config_url = 'push-payload-templates'
    interface = zeit.content.text.interfaces.IJinjaTemplate

    def filterValue(self, value):
        try:
            result = json.loads(value(zeit.content.text.jinja.MockDict()))
        except Exception:
            return True
        else:
            return not result.get('hide_in_vivi')

    def getDefaultTitle(self, value):
        try:
            result = value(zeit.content.text.jinja.MockDict())
            return json.loads(result)['default_title']
        except Exception:
            log.debug('No default title for %s', value.__name__, exc_info=True)
            return ''


PAYLOAD_TEMPLATE_SOURCE = PayloadTemplateSource()


class ToggleDependentField:
    """Field value is required if ``dependent_field`` has value."""

    def __init__(self, dependent_field, **kw):
        super().__init__(**kw)
        self.dependent_field = dependent_field

    def validate(self, value):
        super().validate(value)
        if not value and getattr(self.context, self.dependent_field):
            raise zope.schema.interfaces.RequiredMissing(self.__name__)


class ToggleDependentChoice(ToggleDependentField, zope.schema.Choice):
    pass


class IAccountData(zope.interface.Interface):
    """Convenience access to IPushMessages.message_config entries"""

    facebook_main_text = zope.schema.Text(title=_('Facebook Main Text'), required=False)

    mobile_title = zope.schema.TextLine(title=_('Mobile title'), required=False)
    mobile_text = zope.schema.Text(title=_('Mobile text'), required=False)
    mobile_enabled = zope.schema.Bool(title=_('Enable mobile push'), required=False)

    mobile_uses_image = zope.schema.Bool(title=_('Mobile push with image'), required=False)
    mobile_image = ToggleDependentChoice(
        title=_('Mobile image'),
        description=_('Drag an image group here'),
        source=zeit.content.image.interfaces.imageGroupSource,
        required=False,
        dependent_field='mobile_uses_image',
    )
    mobile_buttons = zope.schema.Choice(
        title=_('Mobile buttons'), source=MOBILE_BUTTONS_SOURCE, required=False
    )
    mobile_payload_template = ToggleDependentChoice(
        title=_('Payload Template'),
        source=PAYLOAD_TEMPLATE_SOURCE,
        required=False,
        dependent_field='mobile_enabled',
    )


class SocialConfig:
    """Provide some convenience methods for social media configuration utilities,
    which encapsulates the zope calls"""

    @classmethod
    def from_account_name(cls, account_name):
        """Return all registered utilities of given class"""
        for utility in zope.component.getAllUtilitiesRegisteredFor(ISocialConfig):
            if isinstance(utility, cls) and utility.name == account_name:
                return utility

    @classmethod
    def from_name(cls, name):
        return zope.component.getUtility(ISocialConfig, name=name)

    @classmethod
    def config(cls, name):
        return zope.app.appsetup.product.getProductConfiguration(cls.product_configuration)[name]
