# vim: fileencoding=utf8 encoding=utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema

import zope.app.security.vocabulary

import zc.form.field

import zeit.cms.workflow.interfaces
import zeit.workflow.source
from zeit.cms.i18n import MessageFactory as _


# The not necessary singleton of a TriState
NotNecessary = zeit.workflow.source.NotNecessary


class IWorkflowStatus(zeit.cms.workflow.interfaces.IPublishInfo):
    """Zeit Workflow interface.

    Currently there is only a *very* simple and static property based workflow
    implemented.

    """

    edited = zope.schema.Choice(
        title=_('status-edited'),
        default=False,
        source=zeit.workflow.source.TriState())

    corrected = zope.schema.Choice(
        title=_('status-corrected'),
        default=False,
        source=zeit.workflow.source.TriState())

    refined = zope.schema.Choice(
        title=_('status-refined'),
        default=False,
        source=zeit.workflow.source.TriState())

    images_added = zope.schema.Choice(
        title=_('status-images-added'),
        default=False,
        source=zeit.workflow.source.TriState())

    urgent = zope.schema.Bool(
        title=_('Urgent'),
        description=_('Select for newsflashs or on a weekend to publish '
                      'without setting corrected/refined/etc.'),
        default=False)

    release_period = zc.form.field.Combination(
        (zope.schema.Datetime(title=_("From"), required=False),
         zope.schema.Datetime(title=_("To"), required=False)),
        title=_('Publication period'),
        description=_('Leave empty for no constraint.'),
        required=False)

    released_from = zope.interface.Attribute(
        "Object is released from this date.")
    released_to = zope.interface.Attribute(
        "Object is released to this date.")

    last_modified_by = zope.schema.Choice(
        title=_('Last modified by'),
        required=False,
        readonly=True,
        source=zope.app.security.vocabulary.PrincipalSource())

    date_last_modified = zope.schema.Datetime(
        title=_('Date last modified'),
        required=False,
        readonly=True)

    date_first_released = zope.schema.Datetime(
        title=_('Date first released'),
        required=False,
        readonly=True)


class IWorkflow(zeit.cms.workflow.interfaces.IPublish, IWorkflowStatus):
    """Combined interface for workflow."""
