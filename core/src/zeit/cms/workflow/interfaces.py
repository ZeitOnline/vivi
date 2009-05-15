# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Workflow interfaces."""

import zope.interface
import zope.schema

import zope.app.security.vocabulary

import zeit.workflow.source
from zeit.cms.i18n import MessageFactory as _


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

    date_first_released = zope.schema.Datetime(
        title=_('Date first released'),
        required=False,
        readonly=True)

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

    def publish():
        """Publish object.

        Before the object is published a BeforePublishEvent is issued.
        After the object has been published a PublishedEvent is issued.
        raises PublishingError if the object cannot be published.

        """

    def retract():
        """Retract an object.

        Before the object is published a BeforeRetractEvent is issued.
        After the object has been published a RetractedEvent is issued.

        """


class IBeforePublishEvent(zope.component.interfaces.IObjectEvent):
    """Issued before an object is published.

    Subscribers may veto publication by rasing an exception.

    """


class IPublishedEvent(zope.component.interfaces.IObjectEvent):
    """Issued when an object was published."""


class IBeforeRetractEvent(zope.component.interfaces.IObjectEvent):
    """Issued before an object is retracted."""


class IRetractedEvent(zope.component.interfaces.IObjectEvent):
    """Issued after an object has been retracted."""


class BeforePublishEvent(zope.component.interfaces.ObjectEvent):
    """Issued before an object is published."""

    zope.interface.implements(IBeforePublishEvent)


class PublishedEvent(zope.component.interfaces.ObjectEvent):
    """Issued when an object was published."""

    zope.interface.implements(IPublishedEvent)


class BeforeRetractEvent(zope.component.interfaces.ObjectEvent):
    """Issued before an object is published."""

    zope.interface.implements(IBeforeRetractEvent)


class RetractedEvent(zope.component.interfaces.ObjectEvent):
    """Issued after an object has been retracted."""

    zope.interface.implements(IRetractedEvent)

