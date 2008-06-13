# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Workflow interfaces."""

import zope.interface
import zope.schema

import zope.app.security.vocabulary

import zc.form.field

import zeit.cms.workflow.interfaces
import zeit.workflow.source
from zeit.cms.i18n import MessageFactory as _


# The not necessary singleton of a TriState
NotNecessary = zeit.workflow.source.NotNecessary

WORKFLOW_NS = u'http://namespaces.zeit.de/CMS/workflow'


class ITimeBasedPublishing(zeit.cms.workflow.interfaces.IPublishInfo):
    """Time based publishing."""

    release_period = zc.form.field.Combination(
        (zope.schema.Datetime(title=_("From"), required=False),
         zope.schema.Datetime(title=_("To"), required=False)),
        title=_('Publication period'),
        description=_('workflow-publication-period-description',
                      u'Leave empty for no constraint.'),
        required=False)


class IContentWorkflow(ITimeBasedPublishing):
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


class IAssetWorkflow(ITimeBasedPublishing):
    """Workflow for assets."""


class IOldCMSStatus(zope.interface.Interface):
    """Support old status flag.

    The old status flag is either "OK" or not presesnt.

    """

    status = zope.schema.TextLine(
        title=u"Status like old CMS (OK, or not present)",
        required=False)
