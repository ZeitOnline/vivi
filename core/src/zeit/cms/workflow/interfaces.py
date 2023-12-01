from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.contentsource
import zope.app.security.vocabulary
import zope.interface
import zope.schema


CAN_PUBLISH_ERROR = 'can-publish-error'
CAN_PUBLISH_WARNING = 'can-publish-warning'
CAN_PUBLISH_SUCCESS = 'can-publish-success'
CAN_RETRACT_ERROR = 'can-retract-error'
CAN_RETRACT_WARNING = 'can-retract-warning'
CAN_RETRACT_SUCCESS = 'can-retract-success'


# During the checkout/checkin cycle() while publishing the object will be most
# likely changed. It therefore would have a modified timestamp _after_ the
# publication timestamp and would be shown as "published with changes", so we
# need to be a little more lenient. (Since we cannot change `modified`, which
# belongs to the DAV server and cannot be written by clients).
PUBLISH_DURATION_GRACE = 60


class PublishingError(Exception):
    """Raised when object publishing fails."""


class RetractingError(Exception):
    """Raised when object retracting fails."""


class IModified(zope.interface.Interface):
    last_modified_by = zope.schema.Choice(
        title=_('Last modified by'),
        required=False,
        readonly=True,
        source=zope.app.security.vocabulary.PrincipalSource(),
    )

    date_last_modified = zope.schema.Datetime(
        title=_('Date last modified'), required=False, readonly=True
    )

    date_last_checkout = zope.schema.Datetime(
        title=_('Date last checked out'), required=False, readonly=True
    )


class IPublishInfo(zope.interface.Interface):
    """Information about published objects."""

    published = zope.schema.Bool(title=_('Published'), readonly=True, default=False)

    date_last_published = zope.schema.Datetime(
        title=_('Date last published'), required=False, default=None, readonly=True
    )

    date_last_published_semantic = zope.schema.Datetime(
        title=_('Last published with semantic change'), required=False, default=None, readonly=True
    )

    date_first_released = zope.schema.Datetime(
        title=_('Date first released'), required=False, readonly=True
    )

    date_print_published = zope.schema.Datetime(
        title=_('Date of print publication'), required=False
    )

    last_published_by = zope.schema.TextLine(
        title=_('Last published by'), required=False, readonly=True
    )

    locked = zope.schema.Bool(
        title=_('Publish lock?'),
        description=_('Please retract first'),
        required=False,
        default=False,
    )

    lock_reason = zope.schema.Text(title=_('Publish lock reason'), required=False)

    error_messages = zope.schema.List(
        title='List of warning and error messages.',
        readonly=True,
        value_type=zope.schema.TextLine(),
    )

    def can_publish():
        """Return whether the object can be published right now.

        returns True if the object can be published, False otherwise.

        """

    def can_retract():
        """Return whether the object can be retracted right now.

        returns True if the object can be retracted, False otherwise.

        """


class IPublicationStatus(zope.interface.Interface):
    published = zope.schema.Choice(
        title=_('Publication state'),
        readonly=True,
        default='published',
        values=('published', 'not-published', 'published-with-changes'),
    )


PRIORITY_HOMEPAGE = 'publish_homepage'
PRIORITY_HIGH = 'publish_highprio'
PRIORITY_DEFAULT = 'publish_default'
PRIORITY_LOW = 'publish_lowprio'
PRIORITY_TIMEBASED = 'publish_timebased'


class IPublishPriority(zope.interface.Interface):
    """Adapts ICMSContent to a PRIORITY_* value."""


@grok.adapter(zope.interface.Interface)
@grok.implementer(IPublishPriority)
def publish_priority_default(context):
    return PRIORITY_DEFAULT


class IPublish(zope.interface.Interface):
    """Interface for publishing/retracting objects."""

    def publish(priority=None, background=True, **kw):
        """Publish object.

        Before the object is published a BeforePublishEvent is issued.
        After the object has been published a PublishedEvent is issued.
        raises PublishingError if the object cannot be published.

        Publishing usually happens asynchronously. PRIORITY_LOW will perform
        the publish task in a separate, single-threaded Queue.
        Pass background=False if you want to execute publishing synchronously.

        `kw` is passed through to the underlying celery task.
        """

    def retract(priority=None, background=True, **kw):
        """Retract an object.

        Before the object is published a BeforeRetractEvent is issued.
        After the object has been published a RetractedEvent is issued.
        raises RetractingError if the object cannot be retracted.

        """

    def publish_multiple(objects, priority=PRIORITY_LOW, background=True):
        """Publish multiple objects in one transaction, given as a list of
        either ICMSContent or uniqueIds.

        (This method doesn't really fit here, on an adapter from ICMSContent,
        but it doesn't make sense to introduce another extension point yet.)
        """

    def retract_multiple(objects, priority=PRIORITY_LOW, background=True):
        """Retract multiple objects in one transaction, given as a list of
        either ICMSContent or uniqueIds.
        """


class IPublisher(zope.interface.Interface):
    """Interface for calling the publisher."""

    def request(self, to_process_list, method):
        """Call the publisher with a list of objects and tell it
        what to do with `method` which is either publish or retract.
        """


class IPublicationDependencies(zope.interface.Interface):
    """Adapter to find the publication dependencies of an object."""

    def get_dependencies():
        """Return a sequence of all dependent objects.

        The sequence contains all objects which need to be published along with the
        adapted object. Dependent containers will be published recursively.
        """

    retract_dependencies = zope.interface.Attribute(
        """\
        If True, retract dependent objects along with the adapted object.
        Usually we cannot know whether an object is used by someone else and
        thus can't retract it, but in some cases this decision can be made."""
    )


class IWithMasterObjectEvent(zope.interface.interfaces.IObjectEvent):
    """Object with master image."""

    master = zope.schema.Choice(
        title='The master object of this event.',
        source=zeit.cms.content.contentsource.cmsContentSource,
    )


class IBeforePublishEvent(IWithMasterObjectEvent):
    """Issued before an object is published.

    Subscribers may veto publication by raising an exception.

    """


class IPublishedEvent(IWithMasterObjectEvent):
    """Issued when an object was published."""


class IBeforeRetractEvent(IWithMasterObjectEvent):
    """Issued before an object is retracted."""


class IRetractedEvent(IWithMasterObjectEvent):
    """Issued after an object has been retracted."""


@zope.interface.implementer(IWithMasterObjectEvent)
class WithMasterObjectEvent(zope.interface.interfaces.ObjectEvent):
    def __init__(self, obj, master):
        super().__init__(obj)
        self.master = master


@zope.interface.implementer(IBeforePublishEvent)
class BeforePublishEvent(WithMasterObjectEvent):
    """Issued before an object is published."""


@zope.interface.implementer(IPublishedEvent)
class PublishedEvent(WithMasterObjectEvent):
    """Issued when an object was published."""


@zope.interface.implementer(IBeforeRetractEvent)
class BeforeRetractEvent(WithMasterObjectEvent):
    """Issued before an object is published."""


@zope.interface.implementer(IRetractedEvent)
class RetractedEvent(WithMasterObjectEvent):
    """Issued after an object has been retracted."""
