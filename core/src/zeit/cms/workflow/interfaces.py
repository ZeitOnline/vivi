from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.contentsource
import zope.app.security.vocabulary
import zope.interface
import zope.schema


CAN_PUBLISH_ERROR = 'can-publish-error'
CAN_PUBLISH_WARNING = 'can-publish-warning'
CAN_PUBLISH_SUCCESS = 'can-publish-success'


# During the checkout/checkin cycle() while publishing the object will be most
# likely changed. It therefore would have a modified timestamp _after_ the
# publication timestamp and would be shown as "published with changes", so we
# need to be a little more lenient. (Since we cannot change `modified`, which
# belongs to the DAV server and cannot be written by clients).
PUBLISH_DURATION_GRACE = 60


class PublishingError(Exception):
    """Raised when object publishing fails."""


class IModified(zope.interface.Interface):

    last_modified_by = zope.schema.Choice(
        title=_('Last modified by'),
        required=False,
        readonly=True,
        source=zope.app.security.vocabulary.PrincipalSource())

    date_last_modified = zope.schema.Datetime(
        title=_('Date last modified'),
        required=False,
        readonly=True)

    date_last_checkout = zope.schema.Datetime(
        title=_('Date last checked out'),
        required=False,
        readonly=True)


class IPublishInfo(zope.interface.Interface):
    """Information about published objects."""

    published = zope.schema.Bool(
        title=_('Published'),
        readonly=True,
        default=False)

    date_last_published = zope.schema.Datetime(
        title=_('Date last published'),
        required=False,
        default=None,
        readonly=True)

    date_last_published_semantic = zope.schema.Datetime(
        title=_('Last published with semantic change'),
        required=False,
        default=None,
        readonly=True)

    date_first_released = zope.schema.Datetime(
        title=_('Date first released'),
        required=False,
        readonly=True)

    date_print_published = zope.schema.Datetime(
        title=_('Date of print publication'),
        required=False,
        readonly=True)

    last_published_by = zope.schema.TextLine(
        title=_('Last published by'),
        required=False,
        readonly=True)

    error_messages = zope.schema.List(
        title=u"List of warning and error messages.",
        readonly=True,
        value_type=zope.schema.TextLine())

    def can_publish():
        """Return whether the object can be published right now.

        returns True if the object can be published, False otherwise.

        """


class IPublicationStatus(zope.interface.Interface):

    published = zope.schema.Choice(
        title=_('Publication state'),
        readonly=True,
        default='published',
        values=('published', 'not-published', 'published-with-changes'))


class IPublish(zope.interface.Interface):
    """Interface for publishing/unpublishing objects."""

    def publish(priority=None, async=True):
        """Publish object.

        Before the object is published a BeforePublishEvent is issued.
        After the object has been published a PublishedEvent is issued.
        raises PublishingError if the object cannot be published.

        Publishing usually happens asynchronously. PRIORITY_LOW will perform
        the publish task in a separate, single-threaded Queue.
        Pass async=False if you want to execute publishing synchronously.

        """

    def retract(priority=None, async=True):
        """Retract an object.

        Before the object is published a BeforeRetractEvent is issued.
        After the object has been published a RetractedEvent is issued.

        """


PRIORITY_HOMEPAGE = 'homepage'
PRIORITY_HIGH = 'highprio'
PRIORITY_DEFAULT = 'default'
PRIORITY_LOW = 'lowprio'
PRIORITY_TIMEBASED = 'timebased'


class IPublishPriority(zope.interface.Interface):
    """Adapts ICMSContent to a PRIORITY_* value."""


@grok.adapter(zope.interface.Interface)
@grok.implementer(IPublishPriority)
def publish_priority_default(context):
    return PRIORITY_DEFAULT


class IWithMasterObjectEvent(zope.component.interfaces.IObjectEvent):
    """Object with master image."""

    master = zope.schema.Choice(
        title=u'The master object of this event.',
        source=zeit.cms.content.contentsource.cmsContentSource)


class IBeforePublishEvent(IWithMasterObjectEvent):
    """Issued before an object is published.

    Subscribers may veto publication by rasing an exception.

    """


class IPublishedEvent(IWithMasterObjectEvent):
    """Issued when an object was published."""


class IBeforeRetractEvent(IWithMasterObjectEvent):
    """Issued before an object is retracted."""


class IRetractedEvent(IWithMasterObjectEvent):
    """Issued after an object has been retracted."""


class WithMasterObjectEvent(zope.component.interfaces.ObjectEvent):

    zope.interface.implements(IWithMasterObjectEvent)

    def __init__(self, obj, master):
        super(WithMasterObjectEvent, self).__init__(obj)
        self.master = master


class BeforePublishEvent(WithMasterObjectEvent):
    """Issued before an object is published."""

    zope.interface.implements(IBeforePublishEvent)


class PublishedEvent(WithMasterObjectEvent):
    """Issued when an object was published."""

    zope.interface.implements(IPublishedEvent)


class BeforeRetractEvent(WithMasterObjectEvent):
    """Issued before an object is published."""

    zope.interface.implements(IBeforeRetractEvent)


class RetractedEvent(WithMasterObjectEvent):
    """Issued after an object has been retracted."""

    zope.interface.implements(IRetractedEvent)
