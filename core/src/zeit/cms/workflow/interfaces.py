# Copyright (c) 2007-2008 gocept gmbh & co. kg
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


class IPublish(zope.interface.Interface):
    """Interface for publishing/unpublishing objects."""

    def publish():
        """Publish object.

        raises PublishingError if the object cannot be published.

        """

    def retract():
        """Retract an object."""


class IBeforePublishEvent(zope.component.interfaces.IObjectEvent):
    """Issued before an object is published."""


class IPublishedEvent(zope.component.interfaces.IObjectEvent):
    """Issued when an object was published."""


class BeforePublishEvent(zope.component.interfaces.ObjectEvent):
    """Issued before an object is published."""

    zope.interface.implements(IBeforePublishEvent)


class PublishedEvent(zope.component.interfaces.ObjectEvent):
    """Issued when an object was published."""

    zope.interface.implements(IPublishedEvent)
